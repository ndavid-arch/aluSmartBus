# Spike #9: Background GPS from a phone browser

**Date:** 10 November 2026
**Tested by:** Ntwali Beni David
**Device:** Google Pixel 6, Chrome
**Test page:** `spikes/gps-test/index.html` (served from Codespaces over HTTPS)

## Question
Does a phone browser keep sending its location when the screen is locked or another app is open? Does the Screen Wake Lock (FR-66) help?

## Results

| Test | Set-up | Longest gap | Result |
|---|---|---|---|
| A | Page open, screen kept on (wake lock), walking ~6 min | 2 s | Continuous readings about every second; accuracy usually ±7 m |
| B | Screen locked with the power button | 52 s (the whole lock time) | Tracking stopped while locked; resumed within seconds of unlocking |
| C | Wake lock on, switched to another app | 497 s (the whole time away) | Tracking stopped while away; accuracy was poor (up to ±143 m) for about 20 s after returning |

## Observations
- The wake lock keeps the screen on, but it does not keep the page running when another app is in front.
- About every 15 s a duplicate reading appears with worse accuracy (±20–40 m), likely a network-based fix mixed with GPS.
- The screen stayed on longer than the phone's timeout whenever the test page was open, even without the wake lock or tracking. A plain web page turned off normally. Cause not found; to recheck once the app is deployed.

## Decision
Keep the **web driver view** for the MVP:
- Keep the screen on during a journey with the Screen Wake Lock (FR-66).
- Warn the driver when they return after a gap ("Location paused while you were away").
- Show students when the location is out of date (#19).
- Ignore readings with accuracy worse than about ±30 m.
- Ask drivers to mount the phone, keep it charging and leave the app open (SRS 2.6).

If the pilot shows drivers often lock the phone or switch apps, build a small native driver app with **Capacitor**, which can track in the background.