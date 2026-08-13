# HANDOFF — Pressure scanning tools (Python) + MATLAB post-processing

Snapshot of work done in this session, for continuity across a repo/session move.

## Context
- This project (`scanningtools_CURRENT`) is a PySide6 desktop app driving a 3-axis
  motorized scanner + PicoScope 5442D MSO for pressure mapping. Companion MATLAB
  post-processing tool lives in a separate repo:
  `C:\Users\Damien Parmentier\Documents\GitHub\stim-pmeasurement-postprocessing`
  (git-synced to the shared corporate GitHub account — untouched by this move).
- This repo (`scanningtools_CURRENT`) was previously not synced anywhere. It is being
  moved to `C:\Users\Damien Parmentier\Documents\GitHub\stim-pmeasurement-scanningtools`,
  replacing old code that used to live there (synced to the corporate account), and is
  being connected to a **new personal repo under the `DamPuls` GitHub account instead**
  — same pattern as the `TargetHeart` project. The old corporate repo is left completely
  untouched (local clone only renamed aside, never deleted; nothing pushed/deleted on
  the GitHub side).

## Architecture (see README.md for user-facing usage)
- `start_app.py` — PySide6 entry point, wires `interface_scan.py` (Qt Designer UI,
  generated from `scan_app_qt.ui`) to `function_app.py`'s `f_app` controller.
- `process_scan.py` (`scanning` class) — orchestrates motor + scope + acquisition +
  trigger generator; owns `run_scan()` / `run_shot_sequence()` main loops.
- `Motors_3Bop.py`, `scope_pico.py`, `acquisition.py`, `generator_trig.py` — hardware
  drivers (serial motor controller, PicoSDK ps5000a scope, block-mode acquisition,
  signal generator trigger).
- `Grid.py` / `Sequence.py` / `Scan.py` — scan geometry: grid definition + boustrophedon
  (`RectDirect`) or spiral (`RectCenter`) traversal order.
- `config/config_scan.ini` — all scan/scope/trigger parameters.

## Changes made this session
1. **Dual-channel acquisition + live plot**: `acquisition.py` now captures Channel B
   alongside A (`self.acq.dataB`). `process_scan.py` has `init_plot()`/`update_plot()`
   for a live-updating matplotlib figure (blue=A, red=B, A drawn on top via `zorder`)
   instead of a new blocking `plt.show()` window per point.
2. **Trigger fix**: `bool_trig_detection=2` (dual A+B "OR" trigger) had a real bug — the
   "disable Channel A via an out-of-range threshold" workaround silently overflowed a
   16-bit ADC struct field (`ctypes` wraps, doesn't error), turning A into a hair-trigger
   instead of disabling it. Added a proper `bool_trig_detection=3` mode in
   `scope_pico.py`'s `config_trigger()` that arms **only** Channel B, never touching A.
3. **2D scan support (Python GUI)**: the three axis selectors in
   `interface_scan.py`/`scan_app_qt.ui` are now independent checkboxes
   (`checkBox_axescan_X/Y/Z`), not mutually-exclusive radio buttons. Check 1 = line
   scan (unchanged behavior), check 2 = plane scan over any axis pair (XY/XZ/YZ).
   `process_scan.py`'s `change_ini_plane(file_ini, step, axis1, axis2, n1, n2)`
   generalizes the old X/Y-only version, centering `Cord_p0` on `[max_point]` along
   **both** selected direction vectors. Wired from `function_app.py`'s `change_ini()`.
   `Grid.py`/`Sequence.py`/`Scan.py`/`run_scan()` needed no changes — they already
   handle `nx>1 AND ny>1` grids natively via the serpentine sequence.
4. **Bug fix**: `function_app.py`'s `change_ini()` used `round(x, 0)` which returns a
   `float` in Python — wrote `"41.0"` into the ini, crashing `Scan.py`'s `int(...)` on
   load. Fixed to `int(round(...))`.
5. **Console noise cleanup**: removed leftover per-line debug `print()`s in
   `Motors_3Bop.py` (`sendCommand`/`readPosition`/`connect`) and `generator_trig.py`
   (`gene_trig`). Added a single clean progress line per acquisition point in
   `process_scan.py` (`print_progress()`): `[N/total] elapsed .. / remaining ~.. |
   X=.. Y=.. Z=..`, with remaining time estimated from the average time-per-point so far.

## MATLAB post-processing (`stim-pmeasurement-postprocessing/DAM/`)
The working single-axis pipeline (`f_process_1axis_scan.m` → `f_convert_pressure_scan_DAM.m`
→ `f_detect_SW_DAM.m` → `f_process_scan_DAM.m` → `compute_*.m`) was **not modified at
all** — it was explicitly off-limits to avoid re-debugging it. `f_process_scan_DAM.m` is
gated to exactly one axis having `n>1`; for a real 2D scan it silently does nothing.

New files added (all `_2D` suffixed, none touch the originals):
- `f_process_scan_2D.m` — new entry point (duplicate of `f_process_1axis_scan.m`'s
  folder loop). Reuses `f_convert_pressure_scan_DAM.m` and `f_detect_SW_DAM.m`
  **unchanged** (they turned out to already be grid-shape-agnostic). After loading each
  folder's config, counts axes with `n>1` and dispatches: 1 → existing
  `f_process_scan_DAM.m` (untouched), 2 → new `f_process_scan_DAM_2D.m`.
- `f_process_scan_DAM_2D.m` — 2D analysis kernel. Maps each point to a `(row,col)` grid
  cell by projecting its *measured* motor coordinates onto the two scan direction
  vectors (robust to any traversal order, since it's pure geometry not acquisition
  order).
- `remove_outliers_2D.m` — 2D neighborhood moving-mean outlier rejection (vs. the 1D
  version's moving mean along scan order, which doesn't mean anything on a plane).
- `compute_max_coordinates_2D.m` — raw peak location only, **no 2D curve fit yet** (no
  spec given for that).
- `compute_momentum_2D.m` — same math as 1D, heatmap plot instead of a line plot.
- `compute_intensities.m` reused **unchanged** — never referenced scan geometry.
- `compute_energy_map_2D.m` — new, no 1D equivalent: builds pressure/intensity
  heatmaps, computes total energy as a **direct 2D surface integral**
  (`Σ Intensity × dx × dy`) rather than the 1D pipeline's revolve-around-the-axis
  approximation (`compute_power.m`'s `π·Σy·dx`), since a real 2D scan doesn't need to
  assume rotational symmetry anymore.

**Status**: user ran `f_process_scan_2D` against a real 2D dataset — it reads files and
produces the heatmaps correctly. Not enough real data yet to validate the energy/power
numbers or go further. **Open/deferred**: no spec yet for a 2D equivalent of the 1D
pipeline's -6dB length/curve-fit/`compute_power.m` (area instead of length, 2D surface
fit for the peak). `write_result_file.m`/`init_result_file.m` (xlsx output) are only
invoked for single-axis results for now (guarded on `isfield(result_data,'fitPMax')`) —
2D scans aren't written to the xlsx yet, pending a column spec.

## Focus Search (Python) — paused, not working, do not resume without addressing the noise issue

**Status: development stopped.** The user watched several live hardware runs (with the
per-line plot described below) and the detected max is frequently an outlier/noise spike
rather than the true peak, so the search does not converge. Left in the codebase as-is
(not deleted) since it's fully additive and doesn't touch any working scan/analysis code
path, but should not be picked back up without first addressing the root cause below.

**Goal**: an automated "Find Focus" button — coordinate-wise coarse-to-fine search that
jogs the motor to the pressure maximum starting from wherever the user parks it, without
touching any existing scan code (explicit non-regression constraint from the user).

**New files, all additive**: `focus_search.py` (search algorithm + live plot),
`sw_detect_py.py` (Python port of `f_detect_SW_DAM.m`), `peak_fit_py.py` (Python port of
`compute_pressure_fit.m`/`compute_length.m` — Gaussian fit with polynomial fallback). UI:
one `QPushButton` added directly in `start_app.py` (not touching `scan_app_qt.ui`/
`interface_scan.py`), wired to `function_app.py`'s `find_focus_app()`.

**Iterations tried, in order, each fixing a real bug found from an actual hardware run**:
1. `run_focus_search` initially skipped `pr.scope_init()` — crashed immediately with
   `AttributeError: 'acquisition_pico' object has no attribute 'maxsamples'`, since that
   module drives `pr.acq`/`pr.trig_shot` directly instead of going through `run_scan()`
   (which always calls `scope_init()` first). Fixed by calling it explicitly.
2. A fitted peak center landing near a physical travel-limit edge (itself caused by a
   saturated sample skewing the fit, see #3) pushed a later scan window's target out of
   the motor's bounds → `MotorError("Motion out of bounds")`, killing an otherwise-
   complete multi-minute search on its very last axis. Fixed by clamping every commanded
   target to `pr.motor.motorParams.limits` before moving.
3. **Channel-A saturation**: the ini's `Channel/ChannelA_range=0.5` (500mV full-scale) is
   tuned for normal scans, but cavitation near true focus produces bursts well above that,
   clipping the ADC at exactly `500.0` — a flat/saturated reading that then anchors the
   curve fit toward a false peak location near the clipped sample. Fixed by forcing a
   5V range for this procedure only (`FORCED_CHANNEL_A_RANGE_V`, in-memory ConfigParser
   override, never written to the ini — `run_scan()` always reloads the ini fresh so
   nothing leaks into a normal scan afterward).
4. **Wrong axis mapping (real bug, caught by the user, not from a crash)**: the original
   code treated "X/Y/Z" as `pr.motor`'s raw physical axes 0/1/2. They are not — X/Y/Z are
   the ini's logical `DirectionX/Y/Z` vectors (X = propagation axis), which can point along
   *any* physical motor (in the test rig, `DirectionX` is wired to the physical motor
   labeled "Y") and in general can combine more than one physical motor at once, exactly
   like `Scan.py`/`Grid.py`'s own `position = p0 + Lx·dirX + Ly·dirY + Lz·dirZ` convention
   for a real 2D scan grid. Rewrote around `_load_direction_vectors()` (normalizes each
   ini direction section to a unit vector) and `_move_to_logical()` (converts a logical
   X/Y/Z offset to the correct physical motor targets, clamped to travel limits) — verified
   offline against the real ini with a stubbed motor.
5. Per the user's request, replaced the original flat coarse→fine two-stage search with
   per-axis multi-stage lists: X (propagation) gets ultra-coarse (5mm step/80mm range) →
   coarse (1mm/40mm) → fine (0.5mm/15mm); Y/Z get coarse (1mm/20mm) → fine (0.2mm/5mm).
   Added a live single-window matplotlib plot (`_plot_scan_line`), redrawn after every
   completed 1D line: measured points, the fitted curve, the detected max (annotated with
   voltage + logical X/Y/Z coordinates), a 2-second pause, and a title naming the cycle/
   axis/stage.

**Root cause of the actual stopping point (not yet fixed)**: even after all of the above,
watching the live plots showed the "detected max" is often a single noisy/spurious sample
rather than the true peak — e.g. one hardware log
(`focus_search_logs/focus_search_20260813_113640.csv`) showed a Y-axis coarse scan
otherwise centered at ~22mm (already converged from the previous cycle) jump to ~13mm
because one sample read 634.6mV against ~200-300mV neighbors, with zero support from
adjacent points — the Gaussian/polynomial fit in `peak_fit_py.fit_peak` has no outlier
rejection and happily fits a curve through/around a lone spike. This is the same *class*
of bug as the outlier-rejection fix already made in the MATLAB 2D pipeline
(`remove_outliers_2D.m`), just never fixed here. A future attempt should almost certainly
add some form of neighbor-consistency check (e.g. reject/down-weight a candidate peak
sample unsupported by its immediate neighbors, or average multiple shots per point) before
trusting a raw single-shot amplitude as the fit input — the per-axis stage restructuring
and axis-mapping fix above are still believed correct and worth keeping, but are not
sufficient on their own since noise robustness was never addressed.

**Second finding (also not fixed)**: the user also flagged seeing negative coordinates in
the plots, "not physically possible." Checked the most recent log
(`focus_search_logs/focus_search_20260813_115044.csv`): the physical `x`/`y`/`z` columns
are never negative — clamping to `pr.motor.motorParams.limits` in `_move_to_logical` does
work (several rows show `x=0.0`, sitting exactly at the floor). The negative values are in
the `commanded` column and the plot's X-axis, which since the axis-mapping fix (#4 above)
is a *logical* offset in mm from wherever the search started, not an absolute physical
coordinate — so `-19.4` there is mathematically fine, just easy to misread as a literal
physical position. However, the log shows a real, related problem: several consecutive
rows request `-19.4, -14.4, -9.4, -4.4mm` while the physical `x` stays pinned at `0.0` the
entire time — i.e. the motor doesn't move at all across those points, they're duplicate
measurements of the same clamped location, and those flat/duplicate samples then feed
directly into the curve fit. That's wasted acquisitions and plausibly makes the outlier
problem above worse (a run of identical points can look like a plateau/edge to the fit).
A future attempt should likely detect a stage whose window would exceed the motor's travel
(from `physical_start`, `dir_vecs`, and `pr.motor.motorParams.limits`) and shrink/re-center
the window up front, rather than silently clamping every out-of-range point one at a time.

## Repo migration (in progress as of this doc)
- Old local clone at `...\GitHub\stim-pmeasurement-scanningtools` renamed aside
  (archived), never deleted, corporate remote on GitHub never touched.
- This repo's content + git history copied to that path, new remote added under
  `DamPuls` (personal account), pushed.
- The original `scanningtools_CURRENT` folder was intentionally **left in place**
  (copied, not moved) to avoid disrupting the active session tied to that path. Safe to
  delete once the new location is confirmed working (reopen the editor there first).
