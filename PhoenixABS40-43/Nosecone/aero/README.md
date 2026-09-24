# Nose v5 aero harness (OpenRocket 24.12, headless)

Both programs run against a **copy** of `PhoenixABS40-43.ork`. Unzip it and set the parachute to
`<deployevent>apogee</deployevent>`, because T5 deploys at apogee, not on the motor's ejection event.
The body tube is patched in code to the as-built T5 stack: 340 mm long, with 245 g of non-nose
dry mass and its CG at 192.7 mm aft of the body top. The source `.ork` is never modified.

```
set CP=C:\Program Files\OpenRocket\jar\OpenRocket-24.12.jar
javac -cp "%CP%" -d . NoseSweep.java Verify.java
java -cp "%CP%;." NoseSweep rocket.ork fixed 30        & rem constant 30 g nose -> drag ranking
java -cp "%CP%;." NoseSweep rocket.ork real 0 2        & rem 2 mm printed shell mass
java -cp "%CP%;." Verify rocket.ork 65 39.6 66.8 20.6 1.5  & rem v5 CAD mass/CG + ballast search
```

Environment knobs: `NS_BODY_G` (non-nose dry mass, g), `NS_LENS` (e.g. `40;65;100`).
Output CSVs in this folder were produced exactly this way on 2026-09-24.
