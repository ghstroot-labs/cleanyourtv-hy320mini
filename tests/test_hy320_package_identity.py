import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APPLICATION_ID = "xyz.ghstroot.cleanyourtv.hy320mini"
JAVA_NAMESPACE = "com.gathin.tvhome"


class Hy320PackageIdentityTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_gradle_separates_application_id_from_java_namespace(self):
        gradle = self.read("launcher/app/build.gradle")
        self.assertIn(f"namespace '{JAVA_NAMESPACE}'", gradle)
        self.assertIn(f"getOrElse('{APPLICATION_ID}')", gradle)

    def test_installers_build_and_target_the_dedicated_package(self):
        for relative in ("launcher/build-and-install.sh", "launcher/build-and-install.ps1"):
            with self.subTest(path=relative):
                content = self.read(relative)
                self.assertIn(APPLICATION_ID, content)
                self.assertIn(f"-PlauncherApplicationId={APPLICATION_ID}", content)
                self.assertNotIn("com.gathin.tvhome/.MainActivity", content)

    def test_theme_tools_and_restart_use_the_same_package(self):
        for relative in ("tools/theme.sh", "tools/theme.ps1", "tools/theme_restart.py"):
            with self.subTest(path=relative):
                self.assertIn(APPLICATION_ID, self.read(relative))

    def test_provider_authority_tracks_application_id(self):
        manifest = self.read("launcher/app/src/main/AndroidManifest.xml")
        self.assertIn('android:authorities="${applicationId}.theme"', manifest)

    def test_build_workflow_builds_the_dedicated_package(self):
        workflow = self.read(".github/workflows/build-hy320.yml")
        self.assertIn(f"-PlauncherApplicationId={APPLICATION_ID}", workflow)
        self.assertIn(":app:testDebugUnitTest", workflow)


    def test_release_signing_never_falls_back_to_debug_key(self):
        gradle = self.read("launcher/app/build.gradle")
        self.assertIn("signingConfig signingConfigs.release", gradle)
        self.assertNotIn("signingConfig signingConfigs.debug", gradle)
        self.assertIn("if (!hasReleaseSigning)", gradle)
        self.assertIn("validateSigningRelease", gradle)

    def test_signed_release_is_manual_and_secret_backed(self):
        workflow = self.read(".github/workflows/build-hy320.yml")
        self.assertIn("build_signed_release", workflow)
        self.assertIn("secrets.ANDROID_KEYSTORE_BASE64", workflow)
        self.assertIn("secrets.ANDROID_KEYSTORE_PASSWORD", workflow)
        self.assertIn("secrets.ANDROID_KEY_ALIAS", workflow)
        self.assertIn(":app:assembleRelease", workflow)
        self.assertIn("Remove temporary signing key", workflow)
        self.assertIn("apksigner\" verify --verbose", workflow)
        self.assertIn("aapt\" dump badging", workflow)

    def test_private_keystore_helper_writes_outside_repository(self):
        helper = self.read("tools/create-hy320-release-keystore.ps1")
        self.assertIn("$env:LOCALAPPDATA", helper)
        self.assertIn("ghstroot-hy320mini-release", helper)
        self.assertIn("Read-Host", helper)
        self.assertNotIn("Set-Clipboard", helper)
        ignore = self.read(".gitignore")
        self.assertIn("*.p12", ignore)
        self.assertIn("*.base64.txt", ignore)


if __name__ == "__main__":
    unittest.main()
