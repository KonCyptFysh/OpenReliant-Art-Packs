"""Check publishing and dependency failures with isolated catalogue fixtures."""

import contextlib
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location("build_site", Path(__file__).with_name("build_site.py"))
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


class CatalogueChecks(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.data = {
            "schema": 2,
            "engine": "0.8.1",
            "groups": [{"id": "ships", "name": "Ships"}],
            "categories": [{"id": "fighters", "name": "Fighters", "group": "ships"}],
            "assets": [{
                "id": "coyote",
                "name": "Coyote",
                "category": "fighters",
                "folder": "packs/coyote",
                "status": "available",
                "defaultLivery": "worn",
                "requires": [],
                "liveries": [
                    self.published("worn", "coyote-worn"),
                    {"id": "factory", "name": "Factory Paint", "status": "coming-soon"},
                ],
            }],
        }
        self.asset = self.data["assets"][0]
        self.worn, self.planned = self.asset["liveries"]
        self.worn.update({
            "preview": "assets/coyote-worn.png",
            "model": "models/coyote-worn.glb",
            "images": [{"src": "assets/coyote-worn.png", "caption": "Worn paint fixture."}],
        })
        self.write("docs/assets/coyote-worn.png", b"Synthetic preview; image decoding is outside this validator.")
        self.write("docs/models/coyote-worn.glb", b"Synthetic model; model decoding is outside this validator.")
        self.write_package("packs/coyote", "coyote-worn")

    @staticmethod
    def published(edition_id, mod_folder):
        tag = edition_id + "-v1.0.0"
        return {
            "id": edition_id,
            "name": edition_id.title(),
            "status": "available",
            "engine": "0.8.1",
            "version": "1.0.0",
            "tag": tag,
            "download": site.RELEASE_ROOT + "download/" + tag + "/artwork.zip",
            "release": site.RELEASE_ROOT + "tag/" + tag,
            "checksum": "ab" * 32,
            "downloadBytes": 1234,
            "modFolder": mod_folder,
        }

    def write(self, name, contents):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(contents, bytes):
            path.write_bytes(contents)
        else:
            path.write_text(contents, encoding="utf-8")
        return path

    def write_package(self, folder, mod_folder, requires="", *, section="Mod"):
        self.write(folder + "/asset-manifest.json", "[]\n")
        return self.write(
            folder + "/mods/" + mod_folder + "/mod.ini",
            f"[{section}]\nName=A display title, not the dependency ID\n"
            "Version=1.0.0\nOpenReliant=0.8.1\n"
            f"rEqUiReS={requires}\n",
        )

    def validate(self, data=None):
        return site.validate(self.root, self.data if data is None else data)

    def test_build_keeps_a_planned_livery_empty_and_preserves_release_metadata(self):
        before = copy.deepcopy(self.data)
        manifest = self.root / "packs/coyote/mods/coyote-worn/mod.ini"
        native_before = manifest.read_bytes()
        self.write("catalog.json", json.dumps(self.data))
        with contextlib.redirect_stdout(io.StringIO()):
            result = site.build(self.root)
        rendered = json.loads((self.root / "docs/catalog.json").read_text())
        self.assertEqual(rendered, before)
        self.assertEqual(result, before)
        self.assertEqual(rendered["assets"][0]["liveries"][1], self.planned)
        self.assertEqual(rendered["assets"][0]["liveries"][0]["engine"], "0.8.1")
        self.assertEqual(manifest.read_bytes(), native_before)

    def test_requires_unions_parent_and_livery_names_case_insensitively(self):
        self.asset["requires"] = ["base-art"]
        self.worn["requires"] = ["BASE-ART", "hud-shapes"]
        self.write_package("packs/coyote", "coyote-worn", " HUD-SHAPES, , Base-Art, ")
        before = copy.deepcopy(self.data)
        self.validate()
        self.assertEqual(self.data, before)

    def test_standalone_pack_requirements_match_native_manifest(self):
        standalone = copy.deepcopy(self.worn)
        standalone.update({
            "id": "coyote", "category": "fighters", "folder": "packs/coyote",
            "requires": ["friends-and-foes"],
        })
        self.data["assets"] = [standalone]
        self.write_package("packs/coyote", "coyote-worn", "FRIENDS-AND-FOES")
        self.validate()

    def test_published_consumer_cannot_require_a_known_unpublished_pack(self):
        self.asset["requires"] = ["FRIENDS-AND-FOES"]
        self.write_package("packs/coyote", "coyote-worn", "friends-and-foes")
        prerequisite = {
            "id": "friends-and-foes", "name": "Friends and Foes",
            "category": "fighters", "status": "coming-soon", "modFolder": "friends-and-foes",
        }
        for prerequisite_first in [True, False]:
            with self.subTest(prerequisite_first=prerequisite_first):
                data = copy.deepcopy(self.data)
                data["assets"].insert(0 if prerequisite_first else 1, prerequisite)
                with self.assertRaisesRegex(ValueError, "required catalogue pack is not published"):
                    self.validate(data)

    def test_published_dependency_can_be_listed_after_its_consumer_in_the_gallery(self):
        self.asset["requires"] = ["FRIENDS-AND-FOES"]
        self.write_package("packs/coyote", "coyote-worn", "friends-and-foes")
        prerequisite = self.published("friends-and-foes", "friends-and-foes")
        prerequisite.update({"category": "fighters", "folder": "packs/friends-and-foes"})
        self.data["assets"].append(prerequisite)
        self.write_package("packs/friends-and-foes", "friends-and-foes")
        self.validate()

    def test_dependency_must_match_a_published_livery_not_just_a_published_parent(self):
        self.asset["requires"] = ["hud-red"]
        self.write_package("packs/coyote", "coyote-worn", "hud-red")
        prerequisite = {
            "id": "hud-art", "category": "fighters", "folder": "packs/hud-art",
            "status": "available", "defaultLivery": "green",
            "liveries": [
                self.published("green", "hud-green"),
                {"id": "red", "status": "coming-soon", "modFolder": "hud-red"},
            ],
        }
        self.data["assets"].append(prerequisite)
        self.write_package("packs/hud-art", "hud-green")
        with self.assertRaisesRegex(ValueError, "required catalogue pack is not published"):
            self.validate()

    def test_planned_consumer_can_declare_a_known_planned_dependency(self):
        self.asset["liveries"] = [self.planned]
        self.asset["status"] = "coming-soon"
        self.asset["defaultLivery"] = "factory"
        self.asset["requires"] = ["friends-and-foes"]
        self.data["assets"].append({
            "id": "friends-and-foes", "category": "fighters",
            "status": "coming-soon", "modFolder": "friends-and-foes",
        })
        self.validate()

    def test_native_and_catalogue_requirements_must_agree_in_both_directions(self):
        for catalogue, native in [(["base-art"], ""), ([], "base-art"), (["base-art"], "other-art")]:
            with self.subTest(catalogue=catalogue, native=native):
                data = copy.deepcopy(self.data)
                data["assets"][0]["requires"] = catalogue
                self.write_package("packs/coyote", "coyote-worn", native)
                with self.assertRaisesRegex(ValueError, "requires must match"):
                    self.validate(data)

    def test_display_name_does_not_satisfy_a_native_folder_dependency(self):
        self.asset["requires"] = ["Friends and Foes Art Pack"]
        self.write_package("packs/coyote", "coyote-worn", "friends-and-foes")
        with self.assertRaisesRegex(ValueError, "requires must match"):
            self.validate()

    def test_dependency_constraints_and_paths_are_not_native_requires_names(self):
        for name in ["base>=1.0", "base^1.0", "base,extra", "../base", "base\\extra"]:
            with self.subTest(name=name):
                data = copy.deepcopy(self.data)
                data["assets"][0]["requires"] = [name]
                with self.assertRaisesRegex(ValueError, "native mod folder name"):
                    self.validate(data)

    def test_case_variants_cannot_duplicate_one_dependency(self):
        self.asset["requires"] = ["base-art", "BASE-ART"]
        with self.assertRaisesRegex(ValueError, "duplicate dependency"):
            self.validate()

    def test_a_pack_cannot_require_itself_through_parent_metadata(self):
        self.asset["requires"] = ["COYOTE-WORN"]
        with self.assertRaisesRegex(ValueError, "cannot require itself"):
            self.validate()

    def test_distinct_assets_cannot_claim_the_same_native_mod_name(self):
        other = copy.deepcopy(self.asset)
        other["id"] = "predator"
        other["liveries"][0]["modFolder"] = "COYOTE-WORN"
        self.data["assets"].append(other)
        with self.assertRaisesRegex(ValueError, "another asset"):
            self.validate()

    def test_unpublished_livery_cannot_expose_published_release_metadata(self):
        for key in ["download", "release", "checksum", "tag", "downloadBytes"]:
            with self.subTest(key=key):
                data = copy.deepcopy(self.data)
                data["assets"][0]["liveries"][1][key] = self.worn[key]
                with self.assertRaisesRegex(ValueError, "unreleased artwork"):
                    self.validate(data)

    def test_explicit_shared_media_is_allowed_without_inheriting_a_release(self):
        self.planned["model"] = self.worn["model"]
        self.validate()
        self.assertNotIn("download", self.planned)
        self.assertNotIn("preview", self.planned)

    def test_livery_asset_cannot_keep_parent_media_or_download_fallbacks(self):
        for key in ["preview", "model", "images", "download", "release"]:
            with self.subTest(key=key):
                data = copy.deepcopy(self.data)
                data["assets"][0][key] = self.worn[key]
                with self.assertRaisesRegex(ValueError, "individual liveries"):
                    self.validate(data)

    def test_default_livery_must_exist(self):
        self.asset["defaultLivery"] = "missing"
        with self.assertRaisesRegex(ValueError, "default livery is missing"):
            self.validate()

    def test_published_asset_cannot_default_to_an_unreleased_livery(self):
        self.asset["defaultLivery"] = "factory"
        with self.assertRaisesRegex(ValueError, "available default livery"):
            self.validate()

    def test_all_planned_liveries_can_have_a_planned_default(self):
        self.asset["liveries"] = [self.planned]
        self.asset["status"] = "coming-soon"
        self.asset["defaultLivery"] = "factory"
        self.validate()

    def test_parent_status_tracks_whether_any_livery_is_available(self):
        for parent_status, all_planned in [("coming-soon", False), ("available", True)]:
            with self.subTest(parent_status=parent_status, all_planned=all_planned):
                data = copy.deepcopy(self.data)
                asset = data["assets"][0]
                asset["status"] = parent_status
                if all_planned:
                    asset["liveries"] = [copy.deepcopy(self.planned)]
                    asset["defaultLivery"] = "factory"
                with self.assertRaisesRegex(ValueError, "status must reflect"):
                    self.validate(data)

    def test_livery_order_does_not_change_the_available_default_or_parent_status(self):
        self.asset["liveries"].reverse()
        self.validate()
        self.assertEqual(self.asset["defaultLivery"], "worn")
        self.assertEqual(self.asset["status"], "available")

    def test_available_pack_requires_its_asset_and_native_manifests(self):
        for name in ["packs/coyote/asset-manifest.json", "packs/coyote/mods/coyote-worn/mod.ini"]:
            with self.subTest(name=name):
                path = self.root / name
                contents = path.read_bytes()
                path.unlink()
                try:
                    with self.assertRaisesRegex(ValueError, "missing (asset manifest|native mod.ini)"):
                        self.validate()
                finally:
                    path.write_bytes(contents)

    def test_preview_and_model_must_exist_as_real_files(self):
        for key in ["preview", "model"]:
            with self.subTest(key=key):
                path = self.root / "docs" / self.worn[key]
                contents = path.read_bytes()
                path.unlink()
                try:
                    with self.assertRaisesRegex(ValueError, "missing preview file"):
                        self.validate()
                finally:
                    path.write_bytes(contents)

    def test_lfs_pointers_cannot_be_published_as_preview_or_model_data(self):
        pointer = b"version https://git-lfs.github.com/spec/v1\noid sha256:" + b"a" * 64 + b"\nsize 100\n"
        for key in ["preview", "model"]:
            with self.subTest(key=key):
                path = self.root / "docs" / self.worn[key]
                contents = path.read_bytes()
                path.write_bytes(pointer)
                try:
                    with self.assertRaisesRegex(ValueError, "Git LFS pointer"):
                        self.validate()
                finally:
                    path.write_bytes(contents)

    def test_additional_gallery_images_are_checked_too(self):
        self.worn["images"].append({"src": "assets/missing-detail.png", "caption": "Wing detail."})
        with self.assertRaisesRegex(ValueError, "missing preview file"):
            self.validate()

    def test_cover_matches_the_first_gallery_image(self):
        self.write("docs/assets/detail.png", b"Synthetic detail.")
        self.worn["images"].insert(0, {"src": "assets/detail.png", "caption": "A different view."})
        with self.assertRaisesRegex(ValueError, "cover must be the first"):
            self.validate()

    def test_duplicate_ids_are_rejected_at_each_catalogue_level(self):
        for level in ["groups", "categories", "assets", "liveries"]:
            with self.subTest(level=level):
                data = copy.deepcopy(self.data)
                records = data["assets"][0]["liveries"] if level == "liveries" else data[level]
                records.append(copy.deepcopy(records[0]))
                with self.assertRaisesRegex(ValueError, "[Dd]uplicate"):
                    self.validate(data)

    def test_repository_paths_cannot_escape_through_media_or_pack_folders(self):
        for field, value in [
            ("preview", "../private.png"),
            ("model", "/tmp/private.glb"),
            ("preview", "assets\\..\\private.png"),
            ("folder", "packs/../../outside"),
        ]:
            with self.subTest(field=field, value=value):
                data = copy.deepcopy(self.data)
                if field == "folder":
                    data["assets"][0][field] = value
                else:
                    edition = data["assets"][0]["liveries"][0]
                    edition.pop("images", None)
                    edition[field] = value
                with self.assertRaisesRegex(ValueError, "inside the repository"):
                    self.validate(data)

    def test_release_download_and_notes_must_name_the_same_final_tag(self):
        for field, value in [
            ("download", site.RELEASE_ROOT + "download/other-tag/artwork.zip"),
            ("download", "https://example.com/artwork.zip"),
            ("release", site.RELEASE_ROOT + "tag/other-tag"),
        ]:
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                data["assets"][0]["liveries"][0][field] = value
                with self.assertRaisesRegex(ValueError, "release download|published tag"):
                    self.validate(data)

    def test_failed_build_leaves_the_previous_published_catalogue_intact(self):
        self.planned["download"] = self.worn["download"]
        self.write("catalog.json", json.dumps(self.data))
        previous = b'{"previous": "published catalogue"}\n'
        published_path = self.write("docs/catalog.json", previous)
        with self.assertRaises(ValueError):
            site.build(self.root)
        self.assertEqual(published_path.read_bytes(), previous)


if __name__ == "__main__":
    unittest.main()
