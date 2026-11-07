# HY320 Projector — CleanYourTV Setup

## Device
- **Model**: HY320 projector (t950s_be311, Google-certified Android TV)
- **Android**: 13 (SDK 33)
- **Firmware**: be311-13 TQ2A.20250729 06:21:20.E1
- **Resolution**: 1280x720, 213dpi

## What was done
1. **Debloated 23 packages** — ad services, app stores, background junk, unused preloaded apps
2. **Installed Apple TV-style launcher** from the original Gathin package; this fork now builds as `xyz.ghstroot.cleanyourtv.hy320mini` with the same Java namespace
3. **Set launcher as default home**, disabled stock launcher (com.htc.htclauncherhighenglishd08)
4. **Enabled AdGuard Private DNS** for ad blocking

## Re-enable an app
```sh
TV_HOST=<tv ip> tools/venv/bin/python tools/tv.py 'pm enable --user 0 <package>'
```

## Restore everything (undo the debloat)
```sh
TV_HOST=<tv ip> tools/restore.sh examples/hy320/debloat.txt com.htc.htclauncherhighenglishd08
```
The stock launcher is passed because `tools/restore.sh` otherwise gives Home back to
`com.google.android.tvlauncher`, the Android TV default, which this projector does not ship - so
the set would come back from an undo with no Home at all.

## Rebuild and reinstall the launcher
```sh
cd launcher
JAVA_HOME=/opt/homebrew/opt/openjdk@17 ANDROID_HOME=/opt/homebrew/share/android-commandlinetools \
  TV_HOST=<tv ip> STOCK_LAUNCHER=none bash build-and-install.sh
```
`STOCK_LAUNCHER=none` because this set's stock launcher, `com.htc.htclauncherhighenglishd08`, is not
one of the launchers `build-and-install.sh` recognises: without it the script stops at "not a stock
launcher this script knows". Home is then set by hand, and the stock launcher stays as a fallback:

```sh
TV_HOST=<tv ip> tools/venv/bin/python tools/tv.py 'cmd package set-home-activity xyz.ghstroot.cleanyourtv.hy320mini/.MainActivity'
```

## Change dock apps or order
Edit `launcher/app/src/main/res/values/config.xml`, the `dock_apps` array, then rebuild.
Or push a theme: edit `examples/hy320/config.json` and run:
```sh
TV_HOST=<tv ip> tools/theme.sh examples/hy320/config.json
```

## Change wallpaper
Set `wallpaper: true` in config.json and add a wallpaper image, or use a theme folder under `themes/`.

AdGuard Private DNS works on this TV.

## Firmware note: HOME.JM
This projector's firmware routes the Home key through the custom
`android.intent.category.HOME.JM` category used by its preloaded JM launcher. The GHSTROOT HY320 Mini
fork now declares `HOME.JM` in `MainActivity`'s existing `MAIN` + `HOME` intent filter, while
retaining the standard `HOME`, `COMMON_HOME` and `DEFAULT` categories. This keeps the device-specific
Home route reproducible from the repository rather than relying on a local manifest patch.

After installing a signed build, verify the firmware's resolver before changing the preferred Home:
`cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME.JM`.
The expected result is `xyz.ghstroot.cleanyourtv.hy320mini/.MainActivity`. Confirm the real remote's
Home key and a reboot on the projector before removing or disabling any fallback launcher.

## Security
This TV has `ro.adb.secure` unset, meaning port 5555 accepts any device on the network without
a prompt. ADB was left open during setup. When done, turn off USB debugging and Network/ADB
debugging on the TV (Settings > Developer Options), revoke USB debugging authorisations, and
reboot. Verify with:
```sh
tools/adb-closed.py <tv ip>
```
