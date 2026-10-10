# HUD-RENDER-01: missing sprite portions during a state sweep

Status: open, user-submitted as upstream #894. Reproduced on official 0.9.0
fa1c098 with HUD 1.10, 10 October 2026. This supersedes the older main-30163d9
status; it does not prove the cause is in the engine.

Run the preserved state-sweep global script with mission991.dte, ship 5, view 2,
1920x1080, tick 220. The screenshot loses portions of fuel/countermeasure,
damage, power and wing icons. Ordinary panel and portrait captures remain clean.
All 911 PNGs are byte-identical to the prior export. No script warnings or
process failure occurred. Persistence during interactive flight is unverified.

Evidence: tracking/integration-0.9.json and local integration-0.9 evidence,
state-sweep-220.png/log/json. Author reply acknowledges two earlier fixes,
#902 and #963, but does not establish that this visible result is their cause.
Keep original and new evidence. Do not claim resolution or submit a duplicate.
