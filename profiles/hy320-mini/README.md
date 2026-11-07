# HY320 Mini personal profile

This profile was reconstructed from the local CleanYourTV launcher backup created on 2026-11-07.

## Files in this profile

| File | Purpose |
|---|---|
| `config.json` | Theme overlay: dock, layout, colours, reduced motion and time-of-day wallpaper settings |
| `order.txt` | Original owner-defined tile order from the backup |
| `cards.json` | Saved module-card decision for the weather card |
| `library_apps.txt` | Manually added Home shortcut from the app library |
| `library_home_removed.txt` | Apps explicitly removed from Home |
| `launcher-state.json` | Effective on-device preferences and restoration notes |
| `backup-manifest.json` | Sanitized inventory of the backup |
| `wallpapers/` | Reserved for private assets; personal images are intentionally deferred |

## Source and effective values

- The profile preserves the observed effective layout: **4 columns**, **70% dock opacity**, and **0 rows below the dock**.
- The dock order remains Netflix, Prime Video, YouTube and Hotstar. The dock header in `order.txt` must continue to match `config.json`.
- `library_apps.txt` and `library_home_removed.txt` preserve separate app-library choices. They are not the same as the `library_apps` theme key.
- The visual settings are based on the upstream `retro` theme, with icon-only buttons disabled to match the backed-up configuration.
- The three time-of-day wallpaper filenames in `config.json` are supplied by the upstream `themes/retro/wallpapers/` directory. They do not need to be extracted from the personal backup.

## Wallpaper handling is deferred

Do not run `extract-wallpapers.ps1` during the current recovery work. Personal wallpaper files and the backed-up manual wallpaper selection will be handled separately later.

**Do not push this directory directly with `tools/theme.ps1` or `tools/theme.sh`.** The upstream theme-push scripts clear the TV's existing wallpaper collection before uploading the selected folder. This profile intentionally does not contain the upstream image binaries.

When we reach theme restoration, prepare a combined local theme by copying the current upstream `themes/retro/` folder and replacing only its `config.json` with this profile's `config.json`. That keeps the upstream Retro wallpaper assets while applying the HY320 Mini layout settings. Do this only after the launcher has been recovered and its package/provider path is confirmed.

The backup recorded `Mario-Peaches.png` as the manually selected wallpaper. Restoring that selection is postponed with the other personal images.

## Order and app-library compatibility

`order.txt` is the launcher's private owner-order file, not a theme key. It is kept as a backup artifact; restoring it requires a supported order-import path or a manual reorder in Launcher Settings. Do not copy it into Android app data with an unrelated file manager.

The package names in the saved order are historical. Apps that are absent, disabled, or no longer expose a TV launch activity may not appear. Verify each app before expecting it to return to Home.

## Privacy

The backup's cached weather text and source from `MainActivity.xml`, the local IP/ADB port from `README.txt`, and internal `settings_revision` / `theme_signature` markers are intentionally excluded.

## Current safety gate

Do not build for installation, push a theme, change the default Home, or disable the stock launcher until all of these are resolved:

1. Restore a working launcher on the projector.
2. Implement and validate the HY320 `HOME.JM` intent handling on the real device.
3. Choose a package identity and configure a persistent signing key.
4. Adapt the installation and theme tools to that package identity.

The device profile is separate from the upstream theme catalogue. It uses documented theme keys and should remain re-applicable after syncing upstream changes.
