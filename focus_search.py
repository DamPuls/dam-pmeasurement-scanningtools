# -*- coding: utf-8 -*-
"""
Coordinate-wise, coarse-to-fine focus search.

Starts from wherever the motor currently is (the user jogs there first with
the existing move buttons - "a starting point given by user"), then for each
axis in turn: a coarse line brackets roughly where the peak is, a fine line
centered on that refines it, using a curve fit (peak_fit_py.fit_peak) rather
than the raw single-highest sample to stay robust to shot-to-shot noise and
flat-topped peaks. Repeats the X/Y/Z cycle until the position stops moving
(or a cycle cap is hit), then leaves the motor at the best-found coordinate.

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

from sw_detect_py import detect_sw
from peak_fit_py import fit_peak

# Matches the MATLAB analysis pipeline's own defaults (f_process_scan_2D.m)
F_SIGNAL_DEFAULT = 2e5
SW_THRESHOLD_DEFAULT = 3e6

COARSE_STEP_MM = 5.0
COARSE_POINTS = 9   # +/- 4 steps around the current center
FINE_STEP_MM = 0.5
FINE_POINTS = 11    # +/- 5 steps around the coarse estimate

MAX_CYCLES = 3
CONVERGENCE_TOL_MM = FINE_STEP_MM  # stop once no axis moves more than this in a cycle

AXIS_ORDER = [1, 2, 0]  # Y, Z (transverse) then X (depth/propagation)


def run_focus_search(pr, on_progress=None):
    """
    pr: the scanning instance (process_scan.py), already connected
        (motor homed, scope configured) - same object f_app.pr already is.
    on_progress: optional callable(str) for status messages.

    Returns a dict: position ([x,y,z] motor coords), widths_m6dB (per axis,
    None if unresolved), total_points, log_path.
    """
    def notify(msg):
        if on_progress:
            on_progress(msg)

    if not getattr(pr.motor, 'connected', False):
        raise RuntimeError("Motor not connected - connect and home it first.")

    best = list(pr.motor.getCurrentPosition())
    log_rows = []
    widths = [None, None, None]
    total_points = 0

    for cycle in range(MAX_CYCLES):
        max_move = 0.0
        for axis in AXIS_ORDER:
            notify(f"Cycle {cycle + 1}: axis {axis} coarse scan around {best[axis]:.2f}...")
            pos, peak = _scan_line(pr, best, axis, best[axis], COARSE_STEP_MM, COARSE_POINTS, log_rows)
            total_points += len(pos)
            coarse_center, _, _ = fit_peak(pos, peak)

            notify(f"Cycle {cycle + 1}: axis {axis} fine scan around {coarse_center:.2f}...")
            pos_f, peak_f = _scan_line(pr, best, axis, coarse_center, FINE_STEP_MM, FINE_POINTS, log_rows)
            total_points += len(pos_f)
            fine_center, _, width = fit_peak(pos_f, peak_f)

            max_move = max(max_move, abs(fine_center - best[axis]))
            best[axis] = fine_center
            widths[axis] = width

        notify(f"Cycle {cycle + 1} done: best=({best[0]:.3f}, {best[1]:.3f}, {best[2]:.3f})")
        if max_move <= CONVERGENCE_TOL_MM:
            notify("Converged.")
            break

    for axis in range(3):
        pr.motor.moveAxisTo(axis, best[axis])

    log_path = _write_log(log_rows)

    return {
        'position': best,
        'widths_m6dB': widths,
        'total_points': total_points,
        'log_path': log_path,
    }


def _scan_line(pr, best, axis, center, step, n_points, log_rows):
    """Sweep one axis around `center`, holding the other two at `best`."""
    half = (n_points - 1) // 2
    positions = []
    peaks = []
    for i in range(n_points):
        offset = (i - half) * step
        target = list(best)
        target[axis] = center + offset
        real_pos, peak, detected = _acquire_one(pr, target)
        positions.append(real_pos[axis])
        peaks.append(peak)
        log_rows.append({
            'axis': axis, 'commanded': target[axis],
            'x': real_pos[0], 'y': real_pos[1], 'z': real_pos[2],
            'peak': peak, 'detected': detected,
        })
    return np.array(positions), np.array(peaks)


def _acquire_one(pr, target_xyz):
    """Move to an absolute (x,y,z) motor coordinate and acquire one shot."""
    for axis in range(3):
        pr.motor.moveAxisTo(axis, target_xyz[axis])

    delay_mvt_acq = 0.1
    try:
        delay_mvt_acq = int(pr.config['delaymvt_acq']['delayms']) * 0.001
    except Exception:
        pass

    pr.acq.running_block()
    position = pr.motor.getCurrentPosition()
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
