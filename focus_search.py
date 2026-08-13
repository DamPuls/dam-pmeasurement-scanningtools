# -*- coding: utf-8 -*-
"""
Coordinate-wise, coarse-to-fine focus search.

"X/Y/Z" here are the ini's logical scan axes - config/config_scan.ini's
DirectionX/DirectionY/DirectionZ vectors (X = propagation axis) - exactly the
convention Scan.py/Grid.py use for a real scan's grid points
(p0 + Lx*dirX + Ly*dirY + Lz*dirZ). A logical axis is NOT necessarily
pr.motor's raw physical axis 0/1/2: dir_axes1/2/3 can combine multiple
physical motors, and their magnitude is just whatever step size the ini
happened to be configured with, not a unit vector - see
_load_direction_vectors. Getting this mapping wrong (treating physical axis
0/1/2 as if they were X/Y/Z directly) was an earlier bug in this module.

Starts from wherever the motor currently is (the user jogs there first with
the existing move buttons - "a starting point given by user"), treating that
as the logical (0,0,0) origin, then for each axis in turn runs a per-axis
list of scan stages (see X_STAGES/YZ_STAGES), each stage's curve-fitted peak
(peak_fit_py.fit_peak) becoming the next, narrower stage's window center -
more robust to shot-to-shot noise and flat-topped peaks than just taking the
raw single-highest sample. X (propagation axis) gets an extra ultra-coarse
first pass since its physical range/depth of field is much larger than
Y/Z's. Repeats the X/Y/Z cycle until the position stops moving (or a cycle
cap is hit), then leaves the motor at the best-found coordinate.

Drives the scan directly through pr.motor / pr.acq / pr.trig_shot - the same
low-level primitives run_scan() uses - without going through Scan/Grid/
Sequence/run_scan() at all, and without modifying any of them. New,
standalone module.

Raw voltage peak amplitude is used as the search metric throughout (not
calibrated pressure) - sufficient for finding *where* the maximum is, since
only relative ordering across points matters here. Calibrated MPa still only
ever comes from the one existing place that does it: the MATLAB analysis
pipeline, run afterward on whatever scan you take at the located focus.
"""
import os
import csv
import time
import datetime

import numpy as np
import matplotlib.pyplot as plt

from sw_detect_py import detect_sw
from peak_fit_py import fit_peak

# Matches the MATLAB analysis pipeline's own defaults (f_process_scan_2D.m)
F_SIGNAL_DEFAULT = 2e5
SW_THRESHOLD_DEFAULT = 3e6

# Per-axis stage lists: (label, step_mm, range_mm), each stage's fitted
# center feeding the next stage's window. X (propagation axis) gets an extra
# ultra-coarse pass first since its true range of motion/depth of field is
# much larger than the transverse (Y/Z) extent.
X_STAGES = [
    ('ultra-coarse', 5.0, 80.0),
    ('coarse', 1.0, 40.0),
    ('fine', 0.5, 15.0),
]
YZ_STAGES = [
    ('coarse', 1.0, 20.0),
    ('fine', 0.2, 5.0),
]

MAX_CYCLES = 3
CONVERGENCE_TOL_MM = 0.5  # stop once no axis moves more than this in a cycle

AXIS_ORDER = [1, 2, 0]  # Y, Z (transverse) then X (depth/propagation)
AXIS_LETTERS = ['X', 'Y', 'Z']

# Forced regardless of the ini's Channel/ChannelA_range: cavitation right at
# focus can spike well above the level a normal scan's range is tuned for,
# and a too-narrow range clips the ADC - seen as flat peak=500.0 samples that
# then skew the peak fit toward a false edge (see earlier focus_search_logs).
FORCED_CHANNEL_A_RANGE_V = 5.0

PLOT_PAUSE_S = 2.0


def run_focus_search(pr, on_progress=None):
    """
    pr: the scanning instance (process_scan.py), already connected
        (motor homed, scope configured) - same object f_app.pr already is.
    on_progress: optional callable(str) for status messages.

    Axes are the ini's logical scan axes (DirectionX/Y/Z), not pr.motor's raw
    physical axis 0/1/2 - see module docstring.

    Returns a dict: position ([motor1,motor2,motor3] physical coords finally
    reached), logical_offset ([X,Y,Z] mm from the search's starting point),
    widths_m6dB (per logical axis, None if unresolved), total_points,
    log_path.
    """
    def notify(msg):
        if on_progress:
            on_progress(msg)

    if not getattr(pr.motor, 'connected', False):
        raise RuntimeError("Motor not connected - connect and home it first.")

    dir_vecs = _load_direction_vectors(pr)
    physical_start = np.array(pr.motor.getCurrentPosition(), dtype=float)

    # Override the ini's channel-A range before configuring the scope - see
    # FORCED_CHANNEL_A_RANGE_V above. Only touches this in-memory ConfigParser
    # copy, not the ini file itself, and run_scan() always re-reads the ini
    # fresh via self.reload(...) before its own scans, so this never leaks
    # into a normal scan afterward.
    pr.sc.config['Channel']['ChannelA_range'] = str(FORCED_CHANNEL_A_RANGE_V)

    # run_scan() always calls this before acquiring; since focus search drives
    # pr.acq/pr.trig_shot directly instead of going through run_scan(), it has
    # to configure the scope itself the same way (sets self.acq.maxsamples,
    # arms the trigger generator, etc.) or the first shot fails with
    # AttributeError: 'acquisition_pico' object has no attribute 'maxsamples'.
    pr.scope_init()

    best = [0.0, 0.0, 0.0]  # logical X/Y/Z offset (mm) from physical_start
    log_rows = []
    widths = [None, None, None]
    total_points = 0

    try:
        for cycle in range(MAX_CYCLES):
            max_move = 0.0
            for axis in AXIS_ORDER:
                center = best[axis]
                width = None
                stages = X_STAGES if axis == 0 else YZ_STAGES
                for label, step, rng in stages:
                    n_points = _stage_n_points(step, rng)
                    notify(f"Cycle {cycle + 1}: {AXIS_LETTERS[axis]} axis {label} scan "
                           f"(step={step}mm, range={rng}mm) around {center:.2f}mm...")
                    pos, peak = _scan_line(pr, physical_start, dir_vecs, best, axis, center, step, n_points, log_rows)
                    total_points += len(pos)
                    center, _, width, x_dense, y_dense = fit_peak(pos, peak)
                    _plot_scan_line(cycle, axis, label, pos, peak, best, x_dense, y_dense)

                max_move = max(max_move, abs(center - best[axis]))
                best[axis] = center
                widths[axis] = width

            notify(f"Cycle {cycle + 1} done: best=(X={best[0]:.3f}, Y={best[1]:.3f}, Z={best[2]:.3f}) mm from start")
            if max_move <= CONVERGENCE_TOL_MM:
                notify("Converged.")
                break

        final_position = _move_to_logical(pr, physical_start, dir_vecs, best)
    except Exception:
        # Write out whatever points were collected before the failure, so a
        # crash mid-search still leaves a log to diagnose from.
        log_path = _write_log(log_rows)
        notify(f"Focus search failed - partial log ({len(log_rows)} points) saved: {log_path}")
        raise

    log_path = _write_log(log_rows)

    return {
        'position': final_position,
        'logical_offset': best,
        'widths_m6dB': widths,
        'total_points': total_points,
        'log_path': log_path,
    }


def _load_direction_vectors(pr):
    """Unit vectors, in physical motor-axis space, for the ini's
    DirectionX/Y/Z - the actual scan axes (e.g. X = propagation axis), which
    are NOT necessarily pr.motor's raw axis 0/1/2 and can combine several
    physical motors. Mirrors Scan.py/Grid.py's own convention: dir_axes1/2/3
    store a (generally non-unit) displacement vector sized to whatever step
    the ini happens to be configured with, so this divides each out by its
    own norm to get a direction-only, step-size-independent unit vector."""
    dir_vecs = []
    for section in ('DirectionX', 'DirectionY', 'DirectionZ'):
        v = np.array([
            float(pr.config[section]['dir_axes1']),
            float(pr.config[section]['dir_axes2']),
            float(pr.config[section]['dir_axes3']),
        ])
        norm = np.linalg.norm(v)
        if norm == 0:
            raise RuntimeError(f"{section} direction vector in the ini is all-zero.")
        dir_vecs.append(v / norm)
    return dir_vecs


def _move_to_logical(pr, physical_start, dir_vecs, logical_xyz):
    """Moves to a logical (X,Y,Z) offset from physical_start (mm along each
    of dir_vecs) and returns the physical motor position actually reached.
    The combined physical target is clamped to the motor's travel limits
    before moving - a fitted peak center landing near a physical edge (e.g.
    from a saturated/clipped sample skewing the fit) would otherwise push a
    later stage's offset out of bounds and moveAxisTo raises MotorError,
    aborting an otherwise-successful multi-minute search."""
    physical_target = physical_start + sum(logical_xyz[a] * dir_vecs[a] for a in range(3))
    limits = pr.motor.motorParams.limits
    physical_target = [min(max(physical_target[m], limits[m][0]), limits[m][1]) for m in range(3)]
    for m in range(3):
        pr.motor.moveAxisTo(m, physical_target[m])
    return pr.motor.getCurrentPosition()


def _stage_n_points(step, rng):
    """Odd point count spanning `rng` symmetrically around the center at
    `step` spacing (matches _scan_line's own +/- half-window convention).
    When rng isn't an exact multiple of step, the achieved span is rounded
    to the nearest whole number of half-steps on each side."""
    half_points = int(round((rng / 2.0) / step))
    return 2 * half_points + 1


def _scan_line(pr, physical_start, dir_vecs, best, axis, center, step, n_points, log_rows):
    """Sweep one logical axis (X/Y/Z per the ini's DirectionX/Y/Z vectors)
    around `center`, holding the other two logical axes at `best`."""
    half = (n_points - 1) // 2
    positions = []
    peaks = []
    for i in range(n_points):
        offset = (i - half) * step
        logical = list(best)
        logical[axis] = center + offset
        real_pos, peak, detected = _acquire_one(pr, physical_start, dir_vecs, logical)
        # Projects the actually-reached physical position back onto this
        # axis's unit direction vector, so a target clamped to the motor's
        # travel limits is recorded at where it truly ended up, not where it
        # was asked to go.
        achieved = float(np.dot(np.array(real_pos) - physical_start, dir_vecs[axis]))
        positions.append(achieved)
        peaks.append(peak)
        log_rows.append({
            'axis': axis, 'commanded': logical[axis],
            'x': real_pos[0], 'y': real_pos[1], 'z': real_pos[2],
            'peak': peak, 'detected': detected,
        })
    return np.array(positions), np.array(peaks)


_search_fig = None
_search_ax = None


def _plot_scan_line(cycle, axis, label, positions, peaks, best, x_dense, y_dense):
    """Draws measured points, the fitted curve, and the detected max for one
    completed 1D line into a single reused figure, then pauses so it's
    actually readable before the next line starts overwriting it."""
    global _search_fig, _search_ax
    if _search_fig is None or not plt.fignum_exists(_search_fig.number):
        _search_fig, _search_ax = plt.subplots(num='Focus search')

    ax = _search_ax
    ax.clear()
    ax.plot(positions, peaks, 'o', color='tab:blue', label='measured')
    ax.plot(x_dense, y_dense, '-', color='tab:orange', label='fitted curve')

    raw_idx = int(np.argmax(peaks))
    raw_pos = positions[raw_idx]
    raw_val = peaks[raw_idx]
    logical_at_max = list(best)
    logical_at_max[axis] = raw_pos
    ax.plot(raw_pos, raw_val, '*', color='tab:red', markersize=16, label='max detected')
    coord_str = ', '.join(f"{AXIS_LETTERS[a]}={logical_at_max[a]:.2f}" for a in range(3))
    ax.annotate(
        f"{raw_val:.1f} mV\n{coord_str} mm",
        (raw_pos, raw_val), textcoords='offset points', xytext=(10, 10))

    fixed_axes = [a for a in range(3) if a != axis]
    fixed_str = ', '.join(f"{AXIS_LETTERS[a]}={best[a]:.2f}mm" for a in fixed_axes)
    ax.set_title(f"Cycle {cycle + 1} - {AXIS_LETTERS[axis]} axis, {label} scan ({fixed_str})")
    ax.set_xlabel(f"{AXIS_LETTERS[axis]} (mm from start)")
    ax.set_ylabel("peak amplitude (mV)")
    ax.legend(loc='best')
    _search_fig.canvas.draw()
    plt.pause(PLOT_PAUSE_S)


def _acquire_one(pr, physical_start, dir_vecs, logical_xyz):
    """Move to a logical (X,Y,Z) offset - mm along each ini-defined
    DirectionX/Y/Z vector, measured from the search's own starting point -
    and acquire one shot."""
    position = _move_to_logical(pr, physical_start, dir_vecs, logical_xyz)

    delay_mvt_acq = 0.1
    try:
        delay_mvt_acq = int(pr.config['delaymvt_acq']['delayms']) * 0.001
    except Exception:
        pass

    pr.acq.running_block()
    time.sleep(delay_mvt_acq)
    pr.trig_shot.gene_trig()
    pr.acq.get_data()

    signal = np.asarray(pr.acq.data)
    time_line = np.asarray(pr.acq.time_line)
    dt = time_line[1] - time_line[0]

    sw, detected = detect_sw(signal, dt, F_SIGNAL_DEFAULT, SW_THRESHOLD_DEFAULT)
    peak = float(np.max(sw)) if detected else float(np.max(signal))

    return position, peak, detected


def _write_log(log_rows):
    log_dir = 'focus_search_logs'
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path = os.path.join(log_dir, f'focus_search_{timestamp}.csv')
    with open(log_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['axis', 'commanded', 'x', 'y', 'z', 'peak', 'detected'])
        writer.writeheader()
        writer.writerows(log_rows)
    return log_path
