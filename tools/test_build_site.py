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
        self.write("docs/index.html", '<link href="style.css?v=old"><script type="module" src="app.js?v=old"></script>')
        self.write("docs/app.js", "import {} from './catalogue-utils.js';\n")
        self.write("docs/catalogue-utils.js", "export const version = 1;\n")
        self.write("docs/style.css", "body { color: white; }\n")

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

    def install_photo_policy(self):
        import hashlib
        self.worn.update(defaultPreview="image", previewType="capture", assetRevision="1.0", previewArtworkRevision="1.0")
        policy = {"profile": "fixture", "categories": ["fighters"], "watch_from": [1.4, -1.4, 1.4],
                  "output_size": [1280, 960], "engine": "fixture engine"}
        record = {"asset": "coyote", "livery": "worn", "gallery_file": self.worn["preview"],
                  "profile": "fixture", "watch_from": policy["watch_from"], "gallery_dimensions": [1280, 960],
                  "engine": "fixture engine", "artwork_revision": "1.0",
                  "runtime_manifest_sha256": hashlib.sha256((self.root / "packs/coyote/asset-manifest.json").read_bytes()).hexdigest(),
                  "gallery_sha256": hashlib.sha256((self.root / "docs" / self.worn["preview"]).read_bytes()).hexdigest()}
        self.write("tracking/gallery-standard.json", json.dumps(policy))
        self.write("tracking/gallery-standard-captures.json", json.dumps({"captures": [record]}))

    def test_ship_photo_guard_accepts_current_capture(self):
        self.install_photo_policy()
        site.validate_ship_photography(self.root, self.data)

    def test_ship_photo_guard_accepts_explicit_asset_engine_override(self):
        self.install_photo_policy()
        policy_path = self.root / 'tracking/gallery-standard.json'
        policy = json.loads(policy_path.read_text())
        policy['engine_overrides'] = {'coyote': 'new official engine'}
        policy_path.write_text(json.dumps(policy))
        record_path = self.root / 'tracking/gallery-standard-captures.json'
        record = json.loads(record_path.read_text())
        record['captures'][0]['engine'] = 'new official engine'
        record_path.write_text(json.dumps(record))
        site.validate_ship_photography(self.root, self.data)

    def test_ship_photo_guard_rejects_another_assets_engine_override(self):
        self.install_photo_policy()
        policy_path = self.root / 'tracking/gallery-standard.json'
        policy = json.loads(policy_path.read_text())
        policy['engine_overrides'] = {'another-ship': 'new official engine'}
        policy_path.write_text(json.dumps(policy))
        record_path = self.root / 'tracking/gallery-standard-captures.json'
        record = json.loads(record_path.read_text())
        record['captures'][0]['engine'] = 'new official engine'
        record_path.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, 'different engine baseline'):
            site.validate_ship_photography(self.root, self.data)

    def test_ship_photo_guard_rejects_old_engine_after_asset_upgrade(self):
        self.install_photo_policy()
        policy_path = self.root / 'tracking/gallery-standard.json'
        policy = json.loads(policy_path.read_text())
        policy['engine_overrides'] = {'coyote': 'new official engine'}
        policy_path.write_text(json.dumps(policy))
        with self.assertRaisesRegex(ValueError, 'different engine baseline'):
            site.validate_ship_photography(self.root, self.data)

    def test_ship_photo_guard_rejects_replacement_without_capture_record(self):
        self.install_photo_policy()
        self.worn["images"][0]["src"] = "assets/user-screenshot.png"
        with self.assertRaisesRegex(ValueError, "unrecorded ship photograph"):
            site.validate_ship_photography(self.root, self.data)

    def test_ship_photo_guard_rejects_outdated_artwork(self):
        self.install_photo_policy()
        self.write("packs/coyote/asset-manifest.json", '[{"updated": true}]')
        with self.assertRaisesRegex(ValueError, "predates the current runtime"):
            site.validate_ship_photography(self.root, self.data)

    def test_ship_photo_guard_rejects_modified_photo(self):
        self.install_photo_policy()
        self.write("docs/" + self.worn["preview"], b"Unrecorded replacement image")
        with self.assertRaisesRegex(ValueError, "no longer matches its capture evidence"):
            site.validate_ship_photography(self.root, self.data)

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

    def test_page_code_changes_get_new_cache_urls(self):
        site.version_site_assets(self.root)
        initial = (self.root / "docs/index.html").read_text()
        app = self.root / "docs/app.js"
        app.write_text(app.read_text() + "// Changed navigation\n")
        site.version_site_assets(self.root)
        changed = (self.root / "docs/index.html").read_text()
        self.assertNotEqual(initial, changed)
        self.assertEqual(initial.split("<script")[0], changed.split("<script")[0])

    def test_module_dependency_changes_refresh_the_entry_script_url(self):
        site.version_site_assets(self.root)
        initial_app = (self.root / "docs/app.js").read_text()
        initial_index = (self.root / "docs/index.html").read_text()
        self.write("docs/catalogue-utils.js", "export const version = 2;\n")
        site.version_site_assets(self.root)
        self.assertNotEqual(initial_app, (self.root / "docs/app.js").read_text())
        self.assertNotEqual(initial_index, (self.root / "docs/index.html").read_text())

    def test_stylesheet_changes_refresh_only_the_stylesheet_url(self):
        site.version_site_assets(self.root)
        initial = (self.root / "docs/index.html").read_text()
        self.write("docs/style.css", "body { color: orange; }\n")
        site.version_site_assets(self.root)
        changed = (self.root / "docs/index.html").read_text()
        self.assertNotEqual(initial, changed)
        self.assertEqual(initial.split("<script")[1], changed.split("<script")[1])

    def test_repeated_builds_keep_identical_cache_urls(self):
        site.version_site_assets(self.root)
        before = {name: (self.root / "docs" / name).read_bytes() for name in ["app.js", "index.html"]}
        site.version_site_assets(self.root)
        self.assertEqual(before, {name: (self.root / "docs" / name).read_bytes() for name in before})

    def test_missing_script_reference_fails_before_writing_page_code(self):
        before = (self.root / "docs/app.js").read_bytes()
        self.write("docs/index.html", '<link href="style.css">')
        with self.assertRaisesRegex(ValueError, "app.js reference"):
            site.version_site_assets(self.root)
        self.assertEqual(before, (self.root / "docs/app.js").read_bytes())

    def test_failed_build_leaves_the_previous_published_catalogue_intact(self):
        self.planned["download"] = self.worn["download"]
        self.write("catalog.json", json.dumps(self.data))
        previous = b'{"previous": "published catalogue"}\n'
        published_path = self.write("docs/catalog.json", previous)
        with self.assertRaises(ValueError):
            site.build(self.root)
        self.assertEqual(published_path.read_bytes(), previous)


    def add_resolution_fixture(self):
        self.worn['defaultResolution'] = '4k'
        self.worn['resolutions'] = []
        for tier,limit in [('1k',1024),('2k',2048),('4k',4096)]:
            variant = {key:self.worn[key] for key in ('download','release','tag','checksum','downloadBytes','version')}
            variant.update(id=tier,maxTextureEdge=limit)
            self.worn['resolutions'].append(variant)

    def test_complete_resolution_set_is_valid(self):
        self.add_resolution_fixture()
        site.validate(self.root,self.data)

    def test_missing_resolution_is_rejected(self):
        self.add_resolution_fixture()
        self.worn['resolutions'].pop()
        with self.assertRaisesRegex(ValueError,'expected 1K'):site.validate(self.root,self.data)

    def test_unverified_resolution_link_is_rejected(self):
        self.add_resolution_fixture()
        self.worn['resolutions'][0]['checksum']=''
        with self.assertRaisesRegex(ValueError,'resolution checksum'):site.validate(self.root,self.data)

    def test_unreleased_resolution_download_is_rejected(self):
        self.add_resolution_fixture()
        self.planned['resolutions']=self.worn['resolutions']
        with self.assertRaisesRegex(ValueError,'released non-HUD'):site.validate(self.root,self.data)

    def test_hud_resolution_download_is_rejected(self):
        self.add_resolution_fixture()
        self.asset['category']='hud';self.data['categories'][0]['id']='hud'
        with self.assertRaisesRegex(ValueError,'non-HUD'):site.validate(self.root,self.data)

    def add_resolution_proof(self):
        self.add_resolution_fixture()
        master = self.root / 'packs/coyote/asset-manifest.json'
        proof = {'editions': {'coyote/worn': {
            'variants': self.worn['resolutions'],
            'master_manifest_sha256': site.hashlib.sha256(master.read_bytes()).hexdigest(),
        }}}
        self.write('tracking/resolution-packs.json', json.dumps(proof))

    def test_changed_master_invalidates_existing_resolution_downloads(self):
        self.add_resolution_proof()
        site.validate(self.root,self.data)
        self.write('packs/coyote/asset-manifest.json', '[{"updated":true}]')
        with self.assertRaisesRegex(ValueError,'stale for this master'):site.validate(self.root,self.data)

    def test_catalogue_resolution_must_match_published_evidence(self):
        self.add_resolution_proof()
        self.worn['resolutions'][0]['checksum']='cd'*32
        with self.assertRaisesRegex(ValueError,'evidence differs'):site.validate(self.root,self.data)

    def test_new_release_cannot_omit_resolution_choices_after_rollout(self):
        self.add_resolution_proof()
        del self.worn['resolutions']
        with self.assertRaisesRegex(ValueError,'needs all resolution'):site.validate(self.root,self.data)

if __name__ == "__main__":
    unittest.main()
