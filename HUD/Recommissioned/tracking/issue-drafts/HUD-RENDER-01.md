# HUD-RENDER-01: missing sprite/text pieces in selected scenes

Status: open local investigation; not submitted upstream and not attributed to
an engine/cache defect yet. Main 30163d9, unmodified.

The dynamic state sweep and an ordinary Mirage review scene lose pieces of
icons, gauges and sometimes text without errors. Normal Coyote flight and the
fixed-position dynamic-state control are clean. One-image-per-frame loading
and leaving native gauges enabled did not remove the fault. Native comparison
captures exist but have different layout/draw load, so they do not identify a
cause. Approved artwork files are unchanged and pass the export audit.

Reproduce with source/compatibility-probes/main-30163d9/state-sweep in the
isolated mission 991, capture around tick 220. Compare fixed-position and
constant-ratio controls; also try Mirage (ship 5) in ordinary mission 991.
See tracking/hud-api-expansion.json and ignored .local/api-expansion/ for logs,
captures and exact engine/runtime pins. Full visual QA remains pending.
