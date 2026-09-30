import os
import re
import glob
import configparser

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

import pressure_convert
from sw_detect_py import detect_sw, _movmean

# Same defaults as the MATLAB pipeline (f_process_scan_2D.m / f_process_1axis_scan.m)
SW_F_SIGNAL = 2e5      # expected SW signal main frequency (Hz)
SW_THRESHOLD_PA = 3e6  # detection threshold (Pa) = 3 MPa
OUTLIER_WINDOW = 5     # remove_outliers.m's window_length

WORKING_CONFIG_PATH = 'config/config_scan.ini'  # the live config the app reads/writes, not the scan's own saved copy


def _write_max_to_config(coord, path=WORKING_CONFIG_PATH):
    """Writes the detected max coordinate into the working config's
    [max_point] section (cordm_axes1/2/3), preserving every other section
    exactly as-is."""
    config = configparser.ConfigParser()
    config.read(path)
    if 'max_point' not in config:
        config['max_point'] = {}
    config['max_point']['cordm_axes1'] = str(coord[0])
    config['max_point']['cordm_axes2'] = str(coord[1])
    config['max_point']['cordm_axes3'] = str(coord[2])
    with open(path, 'w') as f:
        config.write(f)

TYPE_NAMES = ['scan_x', 'scan_y', 'scan_z']

_FILENAME_RE = re.compile(r'ind(\d+)_X_(-?[\d.]+)_Y_(-?[\d.]+)_Z_(-?[\d.]+)_')


def _parse_scan_folder(folder):
    """Port of f_convert_pressure_scan_DAM.m + the shockwave-detection pass
    that normally follows it in the calling MATLAB script (f_process_1axis_scan.m).
    Reads the scan's own saved config + raw ind*.txt files (written by
    process_scan.py's save_config/save_data), converts each to calibrated
    pressure, and runs shockwave detection on each."""
    config = configparser.ConfigParser()
    ini_files = glob.glob(os.path.join(folder, 'config', '*.ini'))
    config.read(ini_files[0])

    krf = float(config['hydro']['krf'])
    temp = float(config['hydro']['temp'])

    nx = int(float(config['Number of points']['nx']))
    ny = int(float(config['Number of points']['ny']))
    nz = int(float(config['Number of points']['nz']))

    dir_x = np.array([float(config['DirectionX']['dir_axes{}'.format(i)]) for i in (1, 2, 3)])
    dir_y = np.array([float(config['DirectionY']['dir_axes{}'.format(i)]) for i in (1, 2, 3)])
    dir_z = np.array([float(config['DirectionZ']['dir_axes{}'.format(i)]) for i in (1, 2, 3)])

    files = glob.glob(os.path.join(folder, 'data', 'ind*.txt'))
    files.sort(key=lambda f: int(_FILENAME_RE.search(os.path.basename(f)).group(1)))

    n = len(files)
    motor_cord = np.zeros((3, n))
    sw = None
    sw_detected = np.zeros(n, dtype=bool)

    for i, f in enumerate(files):
        m = _FILENAME_RE.search(os.path.basename(f))
        motor_cord[0, i] = float(m.group(2))
        motor_cord[1, i] = float(m.group(3))
        motor_cord[2, i] = float(m.group(4))

        raw = np.loadtxt(f)
        dt_s = (raw[1, 0] - raw[0, 0]) * 1e-9
        _, P = pressure_convert.voltage_to_pressure(raw[:, 1], dt_s, krf, temp)
        sw_i, detected_i = detect_sw(P, dt_s, SW_F_SIGNAL, SW_THRESHOLD_PA)
        if sw is None:
            sw = np.zeros((len(sw_i), n))
        sw[:, i] = sw_i
        sw_detected[i] = detected_i

    return dict(motor_cord=motor_cord, sw=sw, sw_detected=sw_detected,
                nx=nx, ny=ny, nz=nz, dir_x=dir_x, dir_y=dir_y, dir_z=dir_z)


def _remove_outliers(vector_axis, max_pressures, sw_detected, window_length=OUTLIER_WINDOW):
    """Port of remove_outliers.m: drops points where no shockwave was
    detected, then iteratively drops points whose deviation from a moving
    mean exceeds a shrinking threshold (0.45 down to 0.2)."""
    devth_min, devth = 0.2, 0.45
    ind_keep = np.where(sw_detected)[0]
    Y = max_pressures[ind_keep]

    while devth >= devth_min:
        y_mean = _movmean(Y, window_length)
        with np.errstate(divide='ignore', invalid='ignore'):
            dev = np.abs(Y - y_mean) / y_mean
        good = dev <= devth
        Y, ind_keep = Y[good], ind_keep[good]
        devth -= 0.05
    return ind_keep


def _compute_length(yval, xval, thdb):
    """Port of compute_length.m: -thdB (e.g. -6dB) width around the peak."""
    yval = np.asarray(yval, dtype=float)
    xval = np.asarray(xval, dtype=float)
    ind_max = int(np.argmax(yval))
    maxval = yval[ind_max]
    y_db = 20 * np.log10(yval / maxval)

    minind = None
    for i in range(0, ind_max + 1):
        if y_db[i] > thdb:
            minind = i - 1  # matches MATLAB's ind-1; can go to -1 ("not found")
            break
    if minind is not None and minind < 0:
        minind = None

    maxind = None
    if minind is not None:
        for i in range(ind_max, len(y_db)):
            if y_db[i] <= thdb:
                maxind = i
                break

    if (minind is not None) and (maxind is not None) and (maxind > minind):
        ind_ldb = np.arange(minind, maxind + 1)
        ldb = xval[maxind] - xval[minind]
        return ind_ldb, ldb, yval[minind:maxind + 1], xval[minind:maxind + 1]
    return np.array([], dtype=int), 0.0, yval[:0], xval[:0]


def _gauss2(x, a1, b1, c1, a2, b2, c2):
    return a1 * np.exp(-((x - b1) / c1) ** 2) + a2 * np.exp(-((x - b2) / c2) ** 2)


def _fit_gauss2(X, Y):
    # A sum of two Gaussians is a genuinely multi-modal fit - MATLAB's
    # fit(X,Y,'gauss2') and scipy's curve_fit can converge to different
    # (each locally valid) optima depending on the start point. Try several
    # plausible start points and keep whichever converges to the lowest
    # residual, rather than trusting a single guess.
    b0 = X[np.argmax(Y)]
    span = (X.max() - X.min()) or 1.0
    a0 = Y.max()
    bounds = ([0, X.min(), 1e-6, 0, X.min(), 1e-6],
              [np.inf, X.max(), span * 2, np.inf, X.max(), span * 2])

    starts = [
        [a0, b0, span / 4, a0 / 2, b0, span / 2],
        [a0, b0, span / 10, a0 / 2, b0, span],
        [a0 / 2, X.min() + span * 0.3, span / 4, a0, b0, span / 4],
        [a0, b0, span / 6, a0 / 3, X.min() + span * 0.7, span / 3],
    ]

    best_popt, best_sse = None, np.inf
    for p0 in starts:
        try:
            popt, _ = curve_fit(_gauss2, X, Y, p0=p0, bounds=bounds, maxfev=20000)
        except RuntimeError:
            continue
        sse = np.sum((_gauss2(X, *popt) - Y) ** 2)
        if sse < best_sse:
            best_sse, best_popt = sse, popt

    return lambda x: _gauss2(np.asarray(x, dtype=float), *best_popt)


def _fit_poly6(X, Y):
    coeffs = np.polyfit(X, Y, 6)
    return lambda x: np.polyval(coeffs, x)


def _enlarge_scan(fitfunc, xfit, yfit, xstep):
    """Port of enlarge_scan.m: extends the fitted x-range left/right,
    stepping in xstep/10 increments, until the fit crosses -6dB on each
    side (so the returned curve fully covers the -6dB width)."""
    maxfit = np.max(yfit)
    scan_width = xfit[-1] - xfit[0]
    step = xstep / 10.0

    xmin = xmax = None
    x = xfit[0]
    while abs(xfit[0] - x) < scan_width:
        y_db = 20 * np.log10(fitfunc(x) / maxfit)
        if y_db < -6:
            xmin = x
            break
        x -= step

    x = xfit[-1]
    while abs(xfit[-1] - x) < scan_width:
        y_db = 20 * np.log10(fitfunc(x) / maxfit)
        if y_db < -6:
            xmax = x
            break
        x += step

    if xmin is not None and xmax is not None:
        return np.linspace(xmin, xmax, 100)
    return xfit


def _compute_pressure_fit(vector_axis, max_pressures, max_pscan, min_pscan, kept_indices):
    """Port of compute_pressure_fit.m (momentum/intensity/power dropped -
    out of scope here). Returns the fit + -6dB length, or a fit-less
    fallback if fewer than 6 kept points."""
    X = vector_axis[kept_indices]
    Y = max_pressures[kept_indices]

    ind_max_y = int(np.argmax(Y))
    max_y = Y[ind_max_y]
    y_db = 20 * np.log10(Y / max_y)
    leftmin = np.min(y_db[:ind_max_y]) if ind_max_y > 0 else np.inf
    rightmin = np.min(y_db[ind_max_y:])
    scan_range_db = max(leftmin, rightmin)

    ldb, ind_ldb = 0.0, np.array([], dtype=int)
    if scan_range_db < -6:
        ind_ldb, ldb, Y, X = _compute_length(Y, X, -6)
        ind_max_y = int(np.argmax(Y))
        max_y = Y[ind_max_y]

    result = dict(scan_range_db=scan_range_db, ldb=ldb, ind_ldb=ind_ldb,
                  X=X, Y=Y, max_y=max_y)

    if len(X) >= 6:
        fitfunc = _fit_gauss2(X, Y)
        xfit = np.linspace(X[0], X[-1], 100)
        yfit = fitfunc(xfit)

        if abs(max_pscan - np.max(np.abs(yfit))) > 3 * max_pscan:
            fitfunc = _fit_poly6(X, Y)
            yfit = fitfunc(xfit)

        xstep = vector_axis[1] - vector_axis[0]
        xfit = _enlarge_scan(fitfunc, xfit, yfit, xstep)
        yfit = fitfunc(xfit)

        ind_max_fit = int(np.argmax(yfit))
        maxfit = yfit[ind_max_fit]
        ind_ldb_fit, ldb_fit, _, _ = _compute_length(yfit, xfit, -6)

        # matches compute_pressure_fit.m's own final result.ldb=ldb_fit - the
        # fitted length supersedes the raw one whenever a fit was computed
        result.update(fitfunc=fitfunc, fitPx=xfit, fitPy=yfit, fitPMax=maxfit,
                       ind_max_fit=ind_max_fit, ldb=ldb_fit, ldb_fit=ldb_fit, ind_ldb_fit=ind_ldb_fit,
                       fitPponPm=round(abs(maxfit / min_pscan), 2))
    else:
        result.update(fitfunc=None, fitPx=None, fitPy=None, fitPMax=max_pscan,
                       ind_max_fit=None, ldb_fit=ldb, ind_ldb_fit=ind_ldb,
                       fitPponPm=round(abs(max_pscan / min_pscan), 2))
    return result


def _compute_max_coordinates(vector_axis, motor_cord, fit_result, ind_max, bool_real, direction):
    """Port of compute_max_coordinates.m: maps the fitted peak's scan-axis
    position back to real 3D motor coordinates, by interpolating between
    the two scan points that bracket it."""
    xfit, yfit = fit_result['fitPx'], fit_result['fitPy']
    maxcoord_fit = None
    xmax_fit = 0.0

    if xfit is not None:
        ind_max_fit = int(np.argmax(yfit))
        xmax_fit = round(float(xfit[ind_max_fit]), 2)

        crossing = np.diff((vector_axis >= xmax_fit).astype(int))
        ind_lim_inf_candidates = np.where(crossing == 1)[0]

        if len(ind_lim_inf_candidates) == 1:
            ind_lim_inf = int(ind_lim_inf_candidates[0])
            ind_lim_sup = ind_lim_inf + 1
            npts = 1000
            sub_coord = np.vstack([
                np.linspace(motor_cord[a, ind_lim_inf], motor_cord[a, ind_lim_sup], npts)
                for a in range(3)
            ])
            o_axes = motor_cord[:, 0]
            ind_moving_axis = np.where(direction != 0)[0]
            if bool_real and len(ind_moving_axis) <= 1:
                sub_vector_axis = sub_coord[ind_moving_axis[0], :]
            else:
                sub_vector_axis = np.sqrt(np.sum((sub_coord - o_axes[:, None]) ** 2, axis=0))

            ind_mindiff = int(np.argmin(np.abs(sub_vector_axis - xmax_fit)))
            maxcoord_fit = np.round(sub_coord[:, ind_mindiff], 2)

    maxcoord_raw = np.round(motor_cord[:, ind_max], 2)
    return maxcoord_fit, maxcoord_raw, xmax_fit


def process_1d_scan(folder, bool_real=True):
    """Port of f_process_scan_DAM.m's 1D-scan branch: pressure conversion +
    shockwave detection + outlier removal + curve fit + max-coordinate
    detection. Momentum/intensity/power are out of scope (dropped).

    Returns None if the folder isn't a valid 1D scan (exactly one of
    nx/ny/nz > 1), matching the MATLAB pipeline's own gating."""
    data = _parse_scan_folder(folder)
    nx, ny, nz = data['nx'], data['ny'], data['nz']
    if not ((nx + ny == 2) or (nx + nz == 2) or (ny + nz == 2)):
        return None

    n = np.array([nx, ny, nz])
    motor_cord = data['motor_cord']
    directions = np.vstack([data['dir_x'], data['dir_y'], data['dir_z']])
    o_axes = motor_cord[:, 0]

    ind_axis = int(np.where(n > 1)[0][0])
    type_measure = TYPE_NAMES[ind_axis]
    direction = directions[ind_axis]

    vector_axis = np.sqrt(np.sum((motor_cord - o_axes[:, None]) ** 2, axis=0))
    vector_axis = np.round(vector_axis, 2)
    ind_moving_axis = np.where(direction != 0)[0]
    if bool_real and len(ind_moving_axis) <= 1:
        vector_axis = motor_cord[ind_moving_axis[0], :]

    sw, sw_detected = data['sw'], data['sw_detected']
    max_pressures = np.max(sw, axis=0) * sw_detected
    min_pressures = np.min(sw, axis=0) * sw_detected

    ind_max = int(np.argmax(max_pressures))
    ind_min = int(np.argmin(min_pressures))
    max_pscan = float(max_pressures[ind_max])
    min_pscan = float(min_pressures[ind_min])

    kept_indices = _remove_outliers(vector_axis, max_pressures, sw_detected)
    fit_result = _compute_pressure_fit(vector_axis, max_pressures, max_pscan, min_pscan, kept_indices)
    maxcoord_fit, maxcoord_raw, xmax_fit = _compute_max_coordinates(
        vector_axis, motor_cord, fit_result, ind_max, bool_real, direction)

    result = dict(type_measure=type_measure, vector_axis=vector_axis,
                  max_pressures=max_pressures, min_pressures=min_pressures,
                  max_pscan=max_pscan, min_pscan=min_pscan,
                  pponpm=round(abs(max_pscan / min_pscan), 2),
                  ind_max=ind_max, ind_min=ind_min, kept_indices=kept_indices,
                  maxcoord_fit=maxcoord_fit, maxcoord_raw=maxcoord_raw, xmax_fit=xmax_fit)
    result.update(fit_result)
    return result


def plot_scan_result(result, save_path=None):
    """Plots peak pressure vs. scan position, with the fit (if available)
    and the detected maximum (value + real motor coordinates) annotated.
    Includes a button to write that max coordinate into the working
    config's [max_point] section."""
    fig, ax = plt.subplots(figsize=(9, 6.5))
    fig.subplots_adjust(bottom=0.18)
    va = result['vector_axis']
    mp_mpa = result['max_pressures'] / 1e6
    kept = result['kept_indices']

    ax.plot(va, mp_mpa, 'rx', ms=8, label='raw (all points)')
    ax.plot(va[kept], mp_mpa[kept], 'bo', ms=6, label='kept (outliers / no-SW removed)')

    if result['fitPx'] is not None:
        ax.plot(result['fitPx'], result['fitPy'] / 1e6, 'g-', lw=2, label='fit')
        peak_val = result['fitPy'][result['ind_max_fit']] / 1e6
        peak_x = result['fitPx'][result['ind_max_fit']]
        coord = result['maxcoord_fit'] if result['maxcoord_fit'] is not None else result['maxcoord_raw']
    else:
        peak_val = result['max_pscan'] / 1e6
        peak_x = va[result['ind_max']]
        coord = result['maxcoord_raw']

    ax.plot(peak_x, peak_val, 'k*', ms=18, zorder=5)
    coord_str = ('X={:.2f}, Y={:.2f}, Z={:.2f}'.format(*coord) if coord is not None else 'n/a')
    # fixed axes-corner placement (not anchored to the peak point) so it never
    # collides with the title regardless of where the peak lands in the plot
    ax.text(0.98, 0.03, 'MAX = {:.2f} MPa\n({})'.format(peak_val, coord_str),
            transform=ax.transAxes, ha='right', va='bottom', fontsize=11,
            bbox=dict(boxstyle='round', fc='white', ec='gray', alpha=0.9))

    ax.set_xlabel('Position along {} (mm)'.format(result['type_measure']))
    ax.set_ylabel('Peak pressure (MPa)')
    ax.set_title('Scan result - {}'.format(result['type_measure']))
    ax.legend(fontsize=9)
    ax.grid(True, linewidth=0.5, alpha=0.6)

    button_ax = fig.add_axes([0.35, 0.03, 0.3, 0.06])
    button = Button(button_ax, 'Write max to config [max_point]')
    fig.write_max_button = button  # keep a reference so it isn't garbage-collected

    def _on_click(event):
        _write_max_to_config(coord)
        button.label.set_text('Written: X={:.2f} Y={:.2f} Z={:.2f}'.format(*coord))
        fig.canvas.draw_idle()

    button.on_clicked(_on_click)

    if save_path:
        fig.savefig(save_path, dpi=140)
    return fig
