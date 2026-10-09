# Named-subtarget test mission reports leaked allocations on shutdown

While checking the subtarget HUD API, I also ran into allocator warnings when closing the test mission.

The attached mission selects the Reliant's Engine component. With no Luau scripts or custom HUD active, saving a screenshot and exiting reports 30 `SafeAllocator` leaked allocations. The process still exits with code 0; this isn't a game crash. The corresponding ordinary fighter-target test doesn't produce those warnings.

Attach `08-subtarget-shutdown-leaks.zip`. It contains only the generated mission mod, its editable source and the test evidence. Use a separate game-data folder with other mods disabled:

```sh
openreliant GAME_DATA --mission 991 --ship 4 --view 2 --size 1920x1080 --no-sound --screenshot-ticks 180 --screenshot subtarget-test.png
```

Expected: clean teardown. Actual: leaked blocks of 56, 112, 168 and 256 bytes in the attached log. The release-safe build prints empty allocation stack traces. I see the same count with and without the API observer.

I haven't established which resource owns these allocations, whether they grow over time, or whether the selected component is the cause rather than another difference in this mission fixture. Could this fixture help identify the missing cleanup? This is a separate runtime diagnostic, not an API-freeze request.

Tested against unmodified upstream main [`57c394b`](https://github.com/OpenReliant/openreliant/commit/57c394b5bb7e9ddc5d171db07f039449854d98c1) on Linux x86_64, built with Zig 0.17.0 in ReleaseSafe mode, at 1920×1080. This build still reports version 0.7.0, so the commit identifies the tested API.
