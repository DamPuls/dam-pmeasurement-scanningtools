# -*- coding: utf-8 -*-
"""
Python port of f_detect_SW_DAM.m (MATLAB, stim-pmeasurement-postprocessing/DAM)
for use in the live focus-search loop, where round-tripping to MATLAB per
acquired point isn't practical. Operates on one raw signal at a time (the
MATLAB version loops over a whole matrix of signals; here the caller already
has one signal per acquired point).

New, standalone module - not used by any existing scan/analysis code path.
"""
import numpy as np
from scipy.signal import find_peaks, peak_widths


def detect_sw(signal, dt, f_signal, threshold, dc_window=(30, 80),
              min_peak_duration=0.2e-6, search_extra_samples=300,
              cavitation_range=150e6):
    """
    Isolate the genuine shockwave pulse within a raw acquisition window.

    signal: 1D array, raw voltage/pressure trace for one acquired point
    dt: sample interval (s)
    f_signal: expected SW signal main frequency (Hz) - bounds plausible peak width
    threshold: MinPeakProminence threshold for findpeaks (same units as signal)
    dc_window: (start, end) sample indices used to estimate/remove DC offset

    Returns (sw_signal, detected):
      sw_signal: signal truncated to the detected SW window (zeroed after it),
                 or the raw (DC-removed) signal unchanged if nothing detected
      detected: bool
    """
    signal = np.asarray(signal, dtype=float)
    n = len(signal)

    dc_mean = np.mean(signal[dc_window[0]:dc_window[1]])
    sig = signal - dc_mean

    max_peak_duration = 1.0 / (2 * f_signal)  # half period of SW
    max_peak_len = int(np.ceil(max_peak_duration / dt))
    min_peak_len = int(np.ceil(min_peak_duration / dt))
    search_width = max_peak_len + search_extra_samples

    ind_zero_up = 0
    ind_zero_down = 0

    peaks, _ = find_peaks(sig, prominence=threshold)
    if len(peaks) > 0:
        widths = peak_widths(sig, peaks, rel_height=0.5)[0]
        valid = np.where((widths <= max_peak_len) & (widths >= min_peak_len))[0]
        if len(valid) > 0:
            loc = peaks[valid[0]]

            if loc + search_width <= n:
                v_up = _movmean(sig[loc:loc + search_width], 30)
                ind_zero_up = _first_sign_change(v_up)
            else:
                ind_zero_up = 0

            if ind_zero_up:
                ind_zero_up = ind_zero_up + loc + 100
                if ind_zero_up + search_width <= n:
                    v_down = _movmean(sig[ind_zero_up:ind_zero_up + search_width], 30)
                    ind_zero_down = _first_sign_change(v_down)
                else:
                    ind_zero_down = 0

                if ind_zero_down:
                    if abs(np.max(sig) - np.min(sig)) > cavitation_range:
                        ind_zero_down = 0  # cavitation-fallout rejection

    if ind_zero_down:
        ind_zero_down = ind_zero_down + ind_zero_up
        sw = sig.copy()
        sw[ind_zero_down:] = 0.0
        return sw, True
    else:
        return sig, False


def _movmean(x, window):
    """Centered moving mean, matching MATLAB's movmean(x, window)."""
    if window <= 1:
        return x.copy()
    kernel = np.ones(window) / window
    pad = window // 2
    xp = np.pad(x, (pad, window - 1 - pad), mode='edge')
    return np.convolve(xp, kernel, mode='valid')[:len(x)]


def _first_sign_change(x):
    """Index (1-based, 0 if none) of the first sign change in x, matching
    MATLAB's find(diff(sign(v)),1)."""
    s = np.sign(x)
    changes = np.nonzero(np.diff(s))[0]
    if len(changes) == 0:
        return 0
    return int(changes[0]) + 1  # 1-based, matching MATLAB's convention used by the caller
