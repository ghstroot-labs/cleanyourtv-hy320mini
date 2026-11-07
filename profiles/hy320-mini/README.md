# HY320 Mini personal profile

This profile was reconstructed from the local CleanYourTV launcher backup created on 2026-11-07.

## Files in this profile

| File | Purpose |
|---|---|
| `config.json` | Theme overlay: dock, layout, colours, reduced motion and timed wallpapers |
| `order.txt` | Original owner-defined tile order from the backup |
| `cards.json` | Saved module-card decision for the weather card |
| `library_apps.txt` | Manually added Home shortcut from the app library |
| `library_home_removed.txt` | Apps explicitly removed from Home |
| `launcher-state.json` | Effective on-device preferences and restoration notes |
| `wallpapers/` | Local-only personal wallpaper assets; image files are excluded from Git |

## Source and effective values

- `files/config.json` supplied the theme overlay and the three time-of-day wallpaper groups.
- `shared_prefs/launcher_settings.xml` stored active local overrides of **4 columns** and **70% dock opacity**. These values took priority over the overlay's 5 columns and 100% opacity, so `config.json` records the effective values to preserve the observed layout after a theme push.
- `files/order.txt` supplied the saved dock order: Netflix, Prime Video, YouTube, Hotstar. The same file records the tile sequence after the dock. Its dock header must continue to match `config.json` or the launcher will ignore the saved order.
- `files/library_apps.txt` and `files/library_home_removed.txt` are preserved as separate app-library choices. They are not the same as `library_apps` in the theme overlay.
- `shared_prefs/launcher_settings.xml` recorded `bundled_theme=retro`; the profile preserves the Retro visual values, with icon-only buttons disabled to match the backup's `config.json`.
- `shared_prefs/launcher_settings.xml` recorded `Mario-Peaches.png` as the selected wallpaper. The time-of-day rotation is also preserved as the theme default.

## Extract the nine private wallpaper files

From the repository root in PowerShell, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\profiles\hy320-mini\extract-wallpapers.ps1
```

The script reads only the nine image entries from the backup ZIP, verifies their expected byte sizes, and writes them into `profiles/hy320-mini/wallpapers/`. It refuses to overwrite existing files unless `-Force` is supplied.

| File | Backup size |
|---|---:|
| `4pm_9pm.jpg` | 236,421 bytes |
| `6am_4pm.jpg` | 174,144 bytes |
| `9pm_6am.jpg` | 279,878 bytes |
| `custom_1793243537158.jpg` | 109,597 bytes |
| `Mario-Olhando-Canos.png` | 1,842,032 bytes |
| `Mario-Peach-Toad.jpeg` | 446,268 bytes |
| `Mario-Peaches.png` | 2,793,239 bytes |
| `Mario-Power-Fire.jpg` | 307,444 bytes |
| `Mario-Yoshi.png` | 2,589,260 bytes |

The three timed images are referenced by `config.json`: morning uses `6am_4pm.jpg`, evening uses `4pm_9pm.jpg`, and night uses `9pm_6am.jpg`.

## Restore the exact wallpaper selection

A theme push clears the on-device manual wallpaper choice. After the theme and wallpaper files are restored, open **Launcher Settings → Wallpaper** and select `Mario-Peaches.png` to reproduce the backed-up selection. Choose **Follow theme** later to resume the morning/evening/night rotation.

## Important compatibility note

`order.txt` is the launcher’s private owner-order file, not a theme key. It is kept here as a backup artifact; restoring it to a running launcher requires a supported order-import path or a manual reorder in Launcher Settings. Do not copy it into Android app data with an unrelated file manager.

The package names in the saved order are historical. Apps that are absent, disabled, or no longer expose a TV launch activity may not appear. Re-enable/verify an app before expecting it to return to Home.

## Privacy

The backup's cached weather text and source from `MainActivity.xml`, the local IP/ADB port from `README.txt`, and internal `settings_revision` / `theme_signature` markers are intentionally excluded. They are not required to recreate the visual profile.

## Applying

Do not push this profile to the projector until the original launcher is recovered, the compatible HY320 HOME handling is resolved, and the wallpaper files have been extracted and checked.

When the launcher is ready and ADB is available:

```sh
TV_HOST=<tv ip> tools/theme.sh profiles/hy320-mini
```

This directory is a device profile, not a new upstream theme listing. The launcher reads the same documented theme keys, so it can be reapplied after syncing the upstream CleanYourTV source.
