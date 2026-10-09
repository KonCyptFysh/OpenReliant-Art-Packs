"""Exercise packaging failure modes without touching any live game assets."""
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("package_mod", Path(__file__).with_name("package_mod.py"))
pack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pack)


class PackageChecks(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        folder = self.root / "mods" / "fixture"
        folder.mkdir(parents=True)
        (folder / "mod.ini").write_text("[Mod]\nName=Fixture\nOpenReliant=0.7\n")
        (folder / "fixture.txt").write_text("Synthetic test content, not game art.\n")
        self.write("README.md", "Synthetic packaging fixture\n")
        self.refresh_manifest()
        self.config = dict(package_name="fixture", version="0.1.0-beta.1", status="ready-for-packaging",
                           hold_reason="test hold", mod_folders=["fixture"], minimum_openreliant="0.7",
                           asset_manifest_sha256=pack.digest(self.root / "asset-manifest.json"),
                           include_documents=["README.md"])
        self.write("release.json", self.config)
        self.report = dict(status="passed", engine_build="synthetic fixture only", tested_platforms=["fixture"],
                           checks=["fixture"], asset_manifest_sha256=self.config["asset_manifest_sha256"])
        self.write("validation.json", self.report)

    def write(self, name, value):
        (self.root / name).write_text(value if isinstance(value, str) else json.dumps(value))

    def refresh_manifest(self):
        self.records = [dict(path=p.relative_to(self.root).as_posix(), bytes=p.stat().st_size, sha256=pack.digest(p))
                        for p in sorted((self.root / "mods").rglob("*")) if p.is_file()]
        self.write("asset-manifest.json", self.records)

    def repin(self):
        sha = pack.digest(self.root / "asset-manifest.json")
        self.config["asset_manifest_sha256"] = sha
        self.report["asset_manifest_sha256"] = sha
        self.write("release.json", self.config)
        self.write("validation.json", self.report)

    def test_reproducible_real_files_and_flat_install_paths(self):
        archive = pack.build(self.root)
        first = pack.digest(archive)
        self.assertEqual(pack.digest(pack.build(self.root)), first)
        with zipfile.ZipFile(archive) as contents:
            self.assertEqual(set(contents.namelist()), {"mods/fixture/mod.ini", "mods/fixture/fixture.txt", "README.md"})
            self.assertEqual(contents.read("mods/fixture/fixture.txt"), (self.root / "mods/fixture/fixture.txt").read_bytes())
        self.assertTrue(archive.with_suffix(".zip.sha256").read_text().startswith(first))

    def test_executable_launcher_permissions_survive_packaging(self):
        launcher = self.root / "inspect.sh"
        launcher.write_text("#!/bin/sh\nexit 0\n")
        launcher.chmod(0o755)
        self.config["include_documents"].append("inspect.sh")
        self.write("release.json", self.config)
        with zipfile.ZipFile(pack.build(self.root)) as contents:
            self.assertEqual(contents.getinfo("inspect.sh").external_attr >> 16, 0o100755)
            self.assertEqual(contents.getinfo("README.md").external_attr >> 16, 0o100644)

    def test_older_component_minimum_is_compatible(self):
        self.write("mods/fixture/mod.ini", "[Mod]\nName=Fixture\nOpenReliant=0.6.3\n")
        self.refresh_manifest()
        self.repin()
        pack.validate(self.root)

    def test_newer_component_minimum_rejected(self):
        self.write("mods/fixture/mod.ini", "[Mod]\nName=Fixture\nOpenReliant=0.7.1\n")
        self.refresh_manifest()
        self.repin()
        with self.assertRaisesRegex(ValueError, "newer OpenReliant"):
            pack.validate(self.root)

    def test_patch_zero_minimum_is_equivalent(self):
        self.write("mods/fixture/mod.ini", "[Mod]\nName=Fixture\nOpenReliant=0.7.0\n")
        self.refresh_manifest()
        self.repin()
        pack.validate(self.root)

    def test_invalid_component_minimum_rejected(self):
        self.write("mods/fixture/mod.ini", "[Mod]\nName=Fixture\nOpenReliant=unknown\n")
        self.refresh_manifest()
        self.repin()
        with self.assertRaisesRegex(ValueError, "Invalid minimum"):
            pack.validate(self.root)

    def test_hold_blocks_release(self):
        self.config["status"] = "hold"
        self.write("release.json", self.config)
        with self.assertRaisesRegex(ValueError, "on hold"):
            pack.build(self.root)
        self.assertFalse((self.root / "dist").exists())

    def test_changed_asset_rejected(self):
        self.write("mods/fixture/fixture.txt", "changed")
        with self.assertRaisesRegex(ValueError, "changed since freeze"):
            pack.validate(self.root)

    def test_stale_runtime_evidence_rejected(self):
        self.report["asset_manifest_sha256"] = "0" * 64
        self.write("validation.json", self.report)
        with self.assertRaisesRegex(ValueError, "different assets"):
            pack.validate(self.root)

    def test_unmanifested_asset_rejected(self):
        self.write("mods/fixture/extra.txt", "unexpected")
        with self.assertRaisesRegex(ValueError, "Unmanifested"):
            pack.validate(self.root)

    def test_lfs_pointer_rejected(self):
        self.write("mods/fixture/fixture.txt", "version https://git-lfs.github.com/spec/v1\noid sha256:test\nsize 99\n")
        self.refresh_manifest()
        self.repin()
        with self.assertRaisesRegex(ValueError, "Git LFS pointer"):
            pack.validate(self.root)

    def test_case_collision_rejected(self):
        self.write("mods/fixture/FIXTURE.txt", "collision")
        self.refresh_manifest()
        self.repin()
        with self.assertRaisesRegex(ValueError, "collision"):
            pack.validate(self.root)

    def test_nested_paths_rejected(self):
        (self.root / "mods/fixture/nested").mkdir()
        self.write("mods/fixture/nested/file.txt", "nested")
        self.refresh_manifest()
        self.repin()
        with self.assertRaisesRegex(ValueError, "flat-file"):
            pack.validate(self.root)

    def test_traversal_path_rejected(self):
        self.records[0]["path"] = "mods/../README.md"
        self.write("asset-manifest.json", self.records)
        self.repin()
        with self.assertRaisesRegex(ValueError, "flat-file"):
            pack.validate(self.root)


if __name__ == "__main__":
    unittest.main()
