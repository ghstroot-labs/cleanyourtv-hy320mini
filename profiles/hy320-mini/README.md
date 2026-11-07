# HY320 Mini personal profile

This profile was reconstructed from the local CleanYourTV launcher backup created on 2026-11-07.

## Source and effective values

- `files/config.json` supplied the theme overlay and the three time-of-day wallpaper groups.
- `shared_prefs/launcher_settings.xml` stored active local overrides of **4 columns** and **70% dock opacity**. These values took priority over the overlay's 5 columns and 100% opacity, so the profile records the effective values to preserve the observed layout after a theme push.
- `files/order.txt` supplied the saved dock order: Netflix, Prime Video, YouTube, Hotstar.
- `shared_prefs/launcher_settings.xml` recorded `bundled_theme=retro`; this profile is a personal variation of the Retro appearance, with the two icon-only options disabled.

## Wallpaper assets required

Copy these files from the private backup into a local `wallpapers/` subfolder before pushing the profile:

- `6am_4pm.jpg`
- `4pm_9pm.jpg`
- `9pm_6am.jpg`
- `Mario-Peaches.png`

The backup also contains additional Mario wallpapers. Keep those files in the private local copy; they are not committed to this public repository.

At backup time, `Mario-Peaches.png` was the explicit on-device wallpaper choice. A theme push clears the on-device wallpaper choice, so after restoring the profile and its images, select `Mario-Peaches.png` again in Launcher Settings > Wallpaper to reproduce that exact static wallpaper. Choosing **Follow theme** returns to the saved morning/evening/night rotation.

## Privacy

The backup's cached weather text and local network address are intentionally excluded. They are not needed to restore the launcher profile and should not be published.

## Applying

Do not push this profile until the listed wallpaper files have been copied into `wallpapers/` and checked. The launcher can then receive it with:

```sh
TV_HOST=<tv ip> tools/theme.sh profiles/hy320-mini
```

This directory is a device profile, not a new upstream theme listing. The launcher still reads the same documented theme keys, so it can be reapplied after syncing the upstream CleanYourTV source.
