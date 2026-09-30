import os
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_CALIB_DIR = os.path.join(_HERE, 'hydrophone_calib')

# --- Onda HFO690 optic parameters (OpticParameters.txt) ---
TREF = 273.15   # K
NC = 1.45552    # fused silica core refractive index
L_NM = 690      # laser wavelength, nm

# --- FindR0FromT.m's Equation-4 polynomial (rho vs T at 0.1MPa),
# from HFO690_Polynomials.mat's e4p/e4mu (7th order, MATLAB polyval
# centering/scaling convention: x_scaled = (T - mu(1))/mu(2)) ---
_E4P = np.array([3.57460194e-03, -1.11394418e-02, 2.27006304e-02, -1.00021216e-01,
                 4.26928166e-01, -3.39803575e+00, -1.43730878e+01, 9.88308718e+02])
_E4MU = (49.38831818, 32.06077145)

_IAPWS_COEFF = np.loadtxt(os.path.join(_CALIB_DIR, 'IAPWS1995_Coefficients.txt'))


def n97(L, rho, T):
    """IAPWS-1997 refractive index of water from wavelength L (nm),
    density rho (kg/m^3), temperature T (K)."""
    rho0, T0, L0 = 1.0e3, 273.15, 589.0
    a0, a1, a2, a3 = 0.244257733, 9.74634476e-3, -3.73234996e-3, 2.68678472e-4
    a4, a5, a6, a7 = 1.58920570e-3, 2.45934259e-3, 0.900704920, -1.66626219e-2
    Luv, Lir = 0.2292020, 5.432937

    rho1 = rho / rho0
    T1 = T / T0
    L1 = L / L0

    R97 = (a0 + a1 * rho1 + a2 * T1 + a3 * L1**2 * T1 + a4 / L1**2
           + a5 / (L1**2 - Luv**2) + a6 / (L1**2 - Lir**2) + a7 * rho1**2)
    K = R97 * rho1
    return np.sqrt((2 * K + 1) / (1 - K))


def rho97(L, n, T):
    """IAPWS-1997 water density (kg/m^3) from wavelength L (nm),
    refractive index n (scalar or array), temperature T (K)."""
    rho0, T0, L0 = 1.0e3, 273.15, 589.0
    a0, a1, a2, a3 = 0.244257733, 9.74634476e-3, -3.73234996e-3, 2.68678472e-4
    a4, a5, a6, a7 = 1.58920570e-3, 2.45934259e-3, 0.900704920, -1.66626219e-2
    Luv, Lir = 0.2292020, 5.432937

    T1 = T / T0
    L1 = L / L0

    p3 = a7
    p2 = a1
    p1 = a0 + a2 * T1 + a3 * L1**2 * T1 + a4 / L1**2 + a5 / (L1**2 - Luv**2) + a6 / (L1**2 - Lir**2)

    n = np.atleast_1d(n)
    p0 = (1 - n**2) / (2 + n**2)

    # Vectorized Newton's method from x0=1, matching MATLAB's fzero(f,1) -
    # same starting point, same root. dR (and so p0) is a small perturbation
    # around the ambient value, so the root stays close to 1 and a fixed,
    # generous iteration count converges to machine precision for every
    # sample at once - orders of magnitude faster than a per-sample
    # np.roots() call (the original approach: ~600ms for a 20k-sample trace,
    # this: sub-millisecond).
    x = np.full_like(p0, 1.0, dtype=float)
    for _ in range(20):
        f = p3 * x**3 + p2 * x**2 + p1 * x + p0
        fp = 3 * p3 * x**2 + 2 * p2 * x + p1
        x = x - f / fp
    return (x * rho0) if x.size > 1 else float(x[0] * rho0)


def P95(rho, T):
    """IAPWS-95 water pressure (Pa) from density rho (kg/m^3), temperature T (K)."""
    Tc, rhoc, R = 647.096, 322.0, 0.46151805e3
    delta = rho / rhoc
    tau = Tc / T

    coeff = _IAPWS_COEFF
    a, b, c, d, n, t = coeff[:, 1], coeff[:, 2], coeff[:, 3], coeff[:, 4], coeff[:, 5], coeff[:, 6]
    aa, bb, ee, gg = coeff[:, 7], coeff[:, 8], coeff[:, 9], coeff[:, 10]
    A, B, C, D = coeff[:, 11], coeff[:, 12], coeff[:, 13], coeff[:, 14]

    # delta/tau may be per-sample arrays; coefficient slices are per-term -
    # broadcast as (..., 1) x (K,) -> (..., K), sum over the last axis.
    delta_b = delta[..., np.newaxis]
    tau_b = tau[..., np.newaxis] if np.ndim(tau) else tau

    i1 = slice(0, 7)
    Frd1 = np.sum(n[i1] * d[i1] * delta_b**(d[i1] - 1) * tau_b**t[i1], axis=-1)

    i2 = slice(7, 51)
    Frd2 = np.sum(n[i2] * np.exp(-delta_b**c[i2]) * delta_b**(d[i2] - 1) * tau_b**t[i2]
                  * (d[i2] - c[i2] * delta_b**c[i2]), axis=-1)

    i3 = slice(51, 54)
    Frd3 = np.sum(n[i3] * delta_b**d[i3] * tau_b**t[i3]
                  * np.exp(-aa[i3] * (delta_b - ee[i3])**2 - bb[i3] * (tau_b - gg[i3])**2)
                  * (d[i3] / delta_b - 2 * aa[i3] * (delta_b - ee[i3])), axis=-1)

    Frd4 = 0.0
    for i in (54, 55):
        theta = (1 - tau) + A[i] * ((delta - 1)**2)**(1 / bb[i] / 2)
        psi = np.exp(-C[i] * (delta - 1)**2 - D[i] * (tau - 1)**2)
        Delta = theta**2 + B[i] * ((delta - 1)**2)**a[i]

        DpsiDdelta = -2 * C[i] * (delta - 1) * psi
        DDeltaDdelta = (delta - 1) * (A[i] * theta * 2 / bb[i] * ((delta - 1)**2)**(1 / 2 / bb[i] - 1)
                                       + 2 * B[i] * a[i] * ((delta - 1)**2)**(a[i] - 1))
        DDelta_biDdelta = b[i] * Delta**(b[i] - 1) * DDeltaDdelta

        Frd4 += (n[i] * Delta**b[i] * psi + n[i] * delta * psi * DDelta_biDdelta
                 + n[i] * Delta**b[i] * delta * DpsiDdelta)

    Frd = Frd1 + Frd2 + Frd3 + Frd4
    return rho * R * T * (1 + delta * Frd)


def find_R0_from_T(T_celsius):
    """Static water/glass reflection coefficient R0 at temperature T (deg C)."""
    x = (T_celsius - _E4MU[0]) / _E4MU[1]
    rho = np.polyval(_E4P, x)
    nw = n97(L_NM, rho, T_celsius + TREF)
    return (nw - NC)**2 / (nw + NC)**2


# --- diffraction kernel (FEAkern690_20190309.txt): freq(MHz), mag(Pa/Pa), phase(deg) ---
def _load_kernel():
    path = os.path.join(_CALIB_DIR, 'FEAkern690_20190309.txt')
    with open(path) as f:
        lines = f.readlines()
    start = next(i for i, l in enumerate(lines) if l.startswith('HEADER_END')) + 1
    data = np.array([[float(x) for x in l.split()] for l in lines[start:] if l.strip()])
    fkern_hz = data[:, 0] * 1e6
    kern = data[:, 1] * np.exp(1j * data[:, 2] * np.pi / 180)
    return fkern_hz, kern


_FKERN_HZ, _KERN = _load_kernel()


def _interp_complex(x_query, x_known, y_known_complex):
    real = np.interp(x_query, x_known, y_known_complex.real)
    imag = np.interp(x_query, x_known, y_known_complex.imag)
    return real + 1j * imag


def _deconv_hfo_fromkern(wfmdat, dt):
    """Port of deconv_hfo_fromkern.m - diffraction correction via the
    loaded kernel, same xfft/xifft (scaled fft/ifft) convention."""
    NFFT = len(wfmdat)
    Fs = 1.0 / dt
    freq = Fs * np.linspace(0, 1, NFFT)  # matches xfft.m exactly (endpoint-inclusive)
    spec = np.fft.fft(wfmdat, NFFT) / NFFT
    spec[0] = 0.0

    Ncut = NFFT // 2 + 1
    if _FKERN_HZ.max() < freq[Ncut - 1]:
        x_known = np.concatenate([_FKERN_HZ, [freq[Ncut - 1]]])
        y_known = np.concatenate([_KERN, [_KERN[-1]]])
    else:
        x_known, y_known = _FKERN_HZ, _KERN
    kerni = _interp_complex(freq[:Ncut], x_known, y_known)

    spec_correct = spec.copy()
    spec_correct[:Ncut] = spec[:Ncut] / kerni
    for jj in range(1, NFFT - Ncut + 1):
        spec_correct[NFFT - jj] = np.conj(spec_correct[jj])

    wfm_correct = np.real(np.fft.ifft(spec_correct, NFFT) * NFFT)
    time_correct = np.linspace(0, 1, NFFT) * (1.0 / (freq[1] - freq[0]) if len(freq) > 1 else 0)
    return wfm_correct, time_correct


def voltage_to_pressure(raw_mV, dt_s, Krf, T_celsius):
    """Single-shot port of HFOpostprocessV3.m's conversion chain (the
    mean_nbr_signal==1 path): raw hydrophone voltage (mV) -> calibrated,
    diffraction-corrected pressure (Pa).

    raw_mV: 1D array, raw voltage samples (mV), as saved in the scan's
        ind*.txt files (2nd column).
    dt_s: sample interval, seconds.
    Krf, T_celsius: from the measurement's own config_scan.ini [hydro]
        section (krf in kV, temp in deg C) - same convention as the
        MATLAB pipeline, NOT hardcoded here.

    Returns (time_correct, pressure_pa), matching HFOpostprocessV3.m's
    own (time_correct, P_correct) outputs.
    """
    raw_mV = np.asarray(raw_mV, dtype=float)
    wfmdat = -raw_mV * 1e-3          # mV -> V, sign flip (matches HFOpostprocessV3.m)
    wfmdat = wfmdat - np.mean(wfmdat)

    dR = wfmdat * 1e-3 / Krf         # V -> kV, /Krf(kV) -> dimensionless reflectivity change

    R0 = find_R0_from_T(T_celsius)
    R = R0 + dR

    nw = NC * (1 - np.sqrt(R)) / (1 + np.sqrt(R))
    rho = rho97(L_NM, nw, TREF + T_celsius)
    P = P95(rho, TREF + T_celsius)

    P_correct, time_correct = _deconv_hfo_fromkern(P, dt_s)
    return time_correct, P_correct
