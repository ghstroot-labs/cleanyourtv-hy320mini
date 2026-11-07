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


if __name__ == "__main__":
    unittest.main()
