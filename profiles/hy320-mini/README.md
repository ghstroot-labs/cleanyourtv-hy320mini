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
- The source backup's historical dock order is preserved in `order.txt`; the active HY320 Mini profile intentionally uses only YouTube (`com.google.android.youtube.tv`) and YouCine (`com.world.youcinetv`). Netflix and SmartTube are deliberately excluded from the dock, and `fill_dock: false` leaves the other two slots empty. The four-column grid remains unchanged.
- `library_apps.txt` and `library_home_removed.txt` preserve separate app-library choices. They are not the same as the `library_apps` theme key.
- The visual settings are based on the upstream `retro` theme, with icon-only buttons disabled to match the backed-up configuration.
- The three time-of-day wallpaper filenames in `config.json` are supplied by the upstream `themes/retro/wallpapers/` directory. They do not need to be extracted from the personal backup.

## Wallpaper handling is deferred

Do not run `extract-wallpapers.ps1` during the current recovery work. Personal wallpaper files and the backed-up manual wallpaper selection will be handled separately later.

**Do not push this directory directly with `tools/theme.ps1` or `tools/theme.sh`.** The upstream theme-push scripts clear the TV's existing wallpaper collection before uploading the selected folder. This profile intentionally does not contain the upstream image binaries.

When we reach theme restoration, prepare a combined local theme by copying the current upstream `themes/retro/` folder and replacing only its `config.json` with this profile's `config.json`. That keeps the upstream Retro wallpaper assets while applying the HY320 Mini layout settings. Do this only after the launcher has been recovered and its package/provider path is confirmed.

The backup recorded `Mario-Peaches.png` as the manually selected wallpaper. Restoring that selection is postponed with the other personal images.

## Order, cards and app-library restoration

The signed HY320 Mini build exposes a narrow, privileged restore path through `ThemeProvider` for exactly four app-private state files: `order.txt`, `cards.json`, `library_apps.txt` and `library_home_removed.txt`. These are written under the package's private `getFilesDir()`; the provider rejects every other private filename and remains protected by `WRITE_SECURE_SETTINGS` (ADB shell only).

The active `order.txt` was adapted to the current dock (YouTube and YouCine, with two empty slots) and preserves the remaining backed-up order. Historical packages that are absent, disabled, or no longer expose a TV launch activity simply do not appear. The module-card decision is retained with its original signer digest, so it only applies if the same app and signing certificate are present. The two app-library lists restore the original owner's explicit add/remove choices.

## Privacy

The backup's cached weather text and source from `MainActivity.xml`, the local IP/ADB port from `README.txt`, and internal `settings_revision` / `theme_signature` markers are intentionally excluded.

## Fork application identity

The original device backup records the historical package `com.gathin.tvhome`. Builds from this fork use the dedicated application ID `xyz.ghstroot.cleanyourtv.hy320mini`, while retaining the Java namespace `com.gathin.tvhome` so upstream class and resource references stay stable.

This is a separate Android application identity. Its first installation will not automatically inherit the original package's private preferences or app data; restoration must be planned and verified separately.

## Current safety gate

Do not build for installation, push a theme, change the default Home, or disable the stock launcher until all of these are resolved:

1. Restore a working launcher on the projector.
2. Implement and validate the HY320 `HOME.JM` intent handling on the real device.
3. Choose a package identity and configure a persistent signing key.
4. Adapt the installation and theme tools to that package identity.

The device profile is separate from the upstream theme catalogue. It uses documented theme keys and should remain re-applicable after syncing upstream changes.
