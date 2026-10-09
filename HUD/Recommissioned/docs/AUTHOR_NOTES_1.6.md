# HUD follow-up notes — not posted

I checked the comms overlap with my HUD disabled. C still opens the menu over
an active portrait, and the number keys work. I'm keeping that behaviour,
so there isn't a request to block comms or change its input API here.
I've fixed the option spacing/first period in my script and enlarged the
objectives panel text.

The separate HD portrait issue remains. A script using radio.scale = 0.25
does bring my 480x400 film down to the normal display size, but it also
shrinks the frame, opening emblem and text. So scripting isn't completely
powerless here, and I shouldn't call an engine change the only conceivable
solution. Rebuilding the radio as a scripted player would be a larger,
unverified workaround; the current HUD API doesn't expose the active film,
speaker or frame, and radio_say includes queued requests.

Could the native film use a 120x100 logical rectangle regardless of source
resolution, leaving its grid/name/timing alone? Using drawImageAs (with the
existing shake/clip behaviour preserved) looks like the small fix. The HD
fixture from the 1.5 notes and the added quarter-scale script demonstrate it.

The t_grendel ammunition and native power-ball reuse notes from 1.5/0.8
still apply. Nothing has been posted from this pass.
