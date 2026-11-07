# HY320 Mini private wallpaper assets

Personal wallpaper handling is intentionally deferred during the projector recovery work.

- Do not extract or publish the personal images now.
- The extraction helper is retained for a later, explicit restoration step.
- This directory is ignored by Git; private artwork must not be committed to the public fork.
- The three time-of-day images used by the profile are already maintained in the upstream `themes/retro/wallpapers/` folder. Future theme restoration must preserve that upstream collection by merging the profile's `config.json` into a copy of the upstream Retro theme.

Do not push this profile directory directly as a theme: the upstream theme-push tool clears the device's wallpaper collection before uploading the files present in the selected theme folder.
