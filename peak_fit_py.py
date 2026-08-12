# -*- coding: utf-8 -*-
"""
Python port of the peak-estimation part of compute_pressure_fit.m /
compute_length.m (MATLAB, stim-pmeasurement-postprocessing/DAM), for use in
the live focus-search loop. Fits a smooth curve to a small set of
(position, peak amplitude) samples from one search line and returns the
estimated true peak position - deliberately not just the raw single-highest
sample, since a flat-topped/noisy peak can have its raw max sit a few mm from
the true (fitted) peak (this is exactly what real scan data showed - see
HANDOFF discussion on the axisplane vs 11_15_17 comparison).

New, standalone module - not used by any existing scan/analysis code path.
"""
import numpy as np
from scipy.optimize import curve_fit


def _gaussian(x, a, mu, sigma, offset):
    return offset + a * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def fit_peak(positions, values, n_dense=200):
    """
    Fit (positions, values) with a Gaussian, falling back to a polynomial
    fit if the Gaussian fit fails or looks unreasonable (mirrors
    compute_pressure_fit.m's gauss2 -> poly6 fallback logic).

    Returns (fitted_peak_position, fitted_peak_value, width_m6dB).
    width_m6dB is None if a -6dB width can't be resolved (e.g. the fit
    never drops 6dB within the sampled range).
    """
    positions = np.asarray(positions, dtype=float)
    values = np.asarray(values, dtype=float)

    raw_max_idx = int(np.argmax(values))
    raw_max_pos = positions[raw_max_idx]
    raw_max_val = values[raw_max_idx]

    x_dense = np.linspace(positions.min(), positions.max(), n_dense)
    y_dense = None

    try:
        span = positions.max() - positions.min()
        sigma0 = max(span / 4.0, 1e-6)
        offset0 = float(np.min(values))
        a0 = raw_max_val - offset0
        p0 = [a0, raw_max_pos, sigma0, offset0]
        popt, _ = curve_fit(_gaussian, positions, values, p0=p0, maxfev=5000)
        candidate = _gaussian(x_dense, *popt)
        if abs(raw_max_val - np.max(candidate)) <= 3 * abs(raw_max_val):
            y_dense = candidate
    except Exception:
        y_dense = None

    if y_dense is None:
        deg = min(6, len(positions) - 1)
        coeffs = np.polyfit(positions, values, deg)
        y_dense = np.polyval(coeffs, x_dense)

    peak_idx = int(np.argmax(y_dense))
    fit_peak_pos = float(x_dense[peak_idx])
    fit_peak_val = float(y_dense[peak_idx])
    width_m6db = _compute_length_m6db(x_dense, y_dense)

    return fit_peak_pos, fit_peak_val, width_m6db


def _compute_length_m6db(x_dense, y_dense, threshold_db=-6.0):
    """-6dB width around the peak, mirrors compute_length.m."""
    peak_idx = int(np.argmax(y_dense))
    max_val = y_dense[peak_idx]
    if max_val <= 0:
        return None

    with np.errstate(divide='ignore', invalid='ignore'):
        y_db = 20 * np.log10(np.abs(y_dense) / max_val)

    left_idx = None
    for i in range(peak_idx, -1, -1):
        if y_db[i] <= threshold_db:
            left_idx = i
            break
    right_idx = None
    for i in range(peak_idx, len(y_dense)):
        if y_db[i] <= threshold_db:
            right_idx = i
            break

    if left_idx is None or right_idx is None:
        return None
    return abs(x_dense[right_idx] - x_dense[left_idx])
