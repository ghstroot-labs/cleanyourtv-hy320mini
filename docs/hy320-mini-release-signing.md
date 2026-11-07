# HY320 Mini: permanent Android release signing

The fork installs as `xyz.ghstroot.cleanyourtv.hy320mini`. Every installable update must keep both that application ID and the same private signing key.

## Create the signing key once

From the repository root in Windows PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\create-hy320-release-keystore.ps1
```

The helper creates a PKCS#12 keystore outside the repository under:

`%LOCALAPPDATA%\GHSTROOT\CleanYourTV\Signing\`

It also writes a Base64 transfer file beside the keystore. The alias is:

`ghstroot-hy320mini-release`

Use a strong password with at least 16 characters. The PKCS#12 keystore and signing key use the same password.

**Back up the original `.p12` file offline in a secure location.** Keep the password in a password manager. Losing the private key or its password means future APKs cannot update the installed app; a new key would require uninstalling/reinstalling and migrating app data.

Do not upload the `.p12` or Base64 file to Git, attach it to an issue, or paste it into chat. Both are private signing material.

## Add three GitHub Actions secrets

Open the repository's **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name | Value |
|---|---|
| `ANDROID_KEYSTORE_BASE64` | Entire one-line contents of `cleanyourtv-hy320mini-release.p12.base64.txt` |
| `ANDROID_KEYSTORE_PASSWORD` | The password entered when generating the keystore |
| `ANDROID_KEY_ALIAS` | `ghstroot-hy320mini-release` |

Use **Secrets**, not Variables. The workflow maps the keystore password to the key password too.

The connected GitHub workflow can read these repository secrets at build time. The secret values themselves must be added by a repository administrator in GitHub Settings.

## Validate a signed release

After all three secrets are saved:

1. Open **Actions → Build HY320 launcher APK → Run workflow**.
2. Select branch `hy320-mini`.
3. Enable `Build an installable release using the private GHSTROOT signing key`.
4. Run the workflow and inspect every step.
5. Download only the `cleanyourtv-hy320mini-signed-release` artifact after success.

Normal pushes and manual runs with that option off continue to produce only the debug CI artifact. It uses a temporary runner key and must not be installed as an update.

The signed-release job verifies that the supplied alias exists, builds the release variant, uploads the signed APK, and removes the temporary keystore file from the runner. The Gradle release variant has no debug-signing fallback: it fails closed if the private signing configuration is absent.

## Installation remains separately gated

A successful signed build does **not** authorize installation. Before the first installation on the HY320, we must:

- recover a working HOME and retain a usable fallback;
- implement and test the firmware-specific `android.intent.category.HOME.JM` route on the actual projector;
- validate first installation under the new package ID and migration of the saved launcher profile;
- verify the app returns as HOME after a reboot and that ADB remains reachable.

Until those checks pass, keep the signed APK as a validation artifact only.
