#!/usr/bin/env python3
"""Validate catalogue metadata, native mod requirements, and static preview files."""

import configparser
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_ROOT = "https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases/"
PRESENTATION_FIELDS = {
    "preview", "model", "images", "previewSource", "previewType", "defaultPreview",
    "previewArtworkRevision", "download", "release", "checksum", "downloadBytes",
    "tag", "version", "assetRevision", "modFolder", "validationSummary",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relative_path(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"{label}: expected a path")
    path = Path(value)
    require(not path.is_absolute() and ".." not in path.parts and "\\" not in value,
            f"{label}: path must stay inside the repository")
    return path


def requirement_names(value, label):
    """Requires contains native directory/HOG basenames, never version expressions."""
    require(isinstance(value, list), f"{label}: requires must be an array of mod folder names")
    names = []
    for name in value:
        require(isinstance(name, str) and name == name.strip() and bool(name),
                f"{label}: empty or untrimmed dependency name")
        require(not re.search(r"[,/\\<>=^~*|\x00-\x1f]", name),
                f"{label}: use a native mod folder name, not a path or version constraint: {name}")
        require(name.casefold() not in names, f"{label}: duplicate dependency {name}")
        names.append(name.casefold())
    return names


def effective_requirements(asset, edition):
    names = requirement_names(asset.get("requires", []), asset["id"])
    if edition is not asset:
        for name in requirement_names(edition.get("requires", []), f"{asset['id']}/{edition['id']}"):
            if name not in names:
                names.append(name)
    return names


def validate_media(root, edition, label):
    media = [edition[key] for key in ("preview", "model") if edition.get(key)]
    if "images" in edition:
        images = edition["images"]
        require(isinstance(images, list), f"{label}: images must be an array")
        if images:
            require(all(isinstance(photo, dict) for photo in images), f"{label}: invalid gallery photo")
            require(edition.get("preview") == images[0].get("src"),
                    f"{label}: cover must be the first gallery photo")
            paths = []
            for photo in images:
                require(isinstance(photo.get("caption"), str) and photo["caption"].strip(),
                        f"{label}: gallery photo needs a caption")
                relative_path(photo.get("src"), label)
                paths.append(photo["src"])
            require(len(set(paths)) == len(paths), f"{label}: duplicate gallery photo")
            media.extend(paths)
    for source in media:
        path = root / "docs" / relative_path(source, label)
        require(path.is_file(), f"{label}: missing preview file {path}")
        with path.open("rb") as stream:
            require(not stream.read(100).startswith(b"version https://git-lfs.github.com/spec/v1"),
                    f"{label}: website media must not be a Git LFS pointer: {path}")


def validate_edition(root, asset, edition, mod_owners):
    label = asset["id"] if edition is asset else f"{asset['id']}/{edition['id']}"
    require(edition.get("status") in {"coming-soon", "available"}, f"{label}: invalid status")
    requirements = effective_requirements(asset, edition)
    mod_folder = edition.get("modFolder")
    if mod_folder:
        requirement_names([mod_folder], label)
        qualifier = mod_folder.casefold()
        require(qualifier not in requirements, f"{label}: a mod cannot require itself")
        require(mod_owners.get(qualifier, asset["id"]) == asset["id"],
                f"{label}: mod folder is also assigned to another asset: {mod_folder}")
        mod_owners[qualifier] = asset["id"]
    if edition["status"] == "available":
        download = edition.get("download", "")
        tag = edition.get("tag", "")
        require(download.startswith(RELEASE_ROOT + "download/"), f"{label}: invalid release download")
        require(bool(tag) and "/releases/download/" + tag + "/" in download,
                f"{label}: download must use its final published tag")
        require(edition.get("release") == RELEASE_ROOT + "tag/" + tag,
                f"{label}: release notes must use the published tag")
        require(re.fullmatch(r"[a-fA-F0-9]{64}", edition.get("checksum", "")) is not None,
                f"{label}: expected a SHA-256 checksum")
        require(isinstance(edition.get("downloadBytes"), int) and edition["downloadBytes"] > 0,
                f"{label}: expected the verified ZIP size")
        folder = relative_path(edition.get("folder", asset.get("folder")), label)
        require((root / folder / "asset-manifest.json").is_file(), f"{label}: missing asset manifest")
        require(bool(mod_folder), f"{label}: a published pack needs its native mod folder name")
        manifest_path = root / folder / "mods" / mod_folder / "mod.ini"
        require(manifest_path.is_file(), f"{label}: missing native mod.ini")
        manifest = configparser.ConfigParser(interpolation=None, strict=False)
        manifest.read(manifest_path, encoding="utf-8-sig")
        require(manifest.has_section("Mod"), f"{label}: native manifest needs [Mod]")
        native_requires = [name.strip() for name in manifest.get("Mod", "Requires", fallback="").split(",") if name.strip()]
        require(set(requirements) == {name.casefold() for name in native_requires},
                f"{label}: catalogue requires must match [Mod] Requires in {manifest_path}")
    else:
        require(not any(edition.get(key) for key in ("download", "release", "checksum", "tag", "downloadBytes")),
                f"{label}: unreleased artwork must not expose a published download")
    validate_media(root, edition, label)


def validate(root, data):
    root = Path(root)
    require(data.get("schema") == 2, "Expected catalogue schema 2")
    groups = {group["id"] for group in data["groups"]}
    require(len(groups) == len(data["groups"]), "Duplicate group ID")
    categories = {category["id"] for category in data["categories"]}
    require(len(categories) == len(data["categories"]), "Duplicate category ID")
    for category in data["categories"]:
        require(category.get("group") in groups, f"{category['id']}: unknown group")
    ids, mod_owners, release_requirements = set(), {}, []
    available_mods = set()
    for asset in data["assets"]:
        label = asset["id"]
        require(label not in ids, f"Duplicate asset ID: {label}")
        ids.add(label)
        require(asset.get("category") in categories, f"{label}: unknown category")
        require(asset.get("status") in {"coming-soon", "available"}, f"{label}: invalid status")
        require(isinstance(asset.get("countsTowardProgress", True), bool), f"{label}: invalid progress scope")
        if not asset.get("countsTowardProgress", True):
            require(asset.get("scopeStatus") == "pending-audit", f"{label}: explain excluded progress scope")
        if asset.get("folder"):
            relative_path(asset["folder"], label)
        if "liveries" in asset:
            editions = asset["liveries"]
            require(isinstance(editions, list) and bool(editions), f"{label}: expected at least one livery")
            livery_ids = [edition["id"] for edition in editions]
            require(len(set(livery_ids)) == len(livery_ids), f"{label}: duplicate livery ID")
            require(asset.get("defaultLivery") in livery_ids, f"{label}: default livery is missing")
            require(not (PRESENTATION_FIELDS & asset.keys()),
                    f"{label}: media and release metadata belong to individual liveries")
            available = any(edition.get("status") == "available" for edition in editions)
            require(asset["status"] == ("available" if available else "coming-soon"),
                    f"{label}: asset status must reflect its available liveries")
            default = next(edition for edition in editions if edition["id"] == asset["defaultLivery"])
            require(not available or default.get("status") == "available",
                    f"{label}: choose an available default livery for a published asset")
        else:
            require("defaultLivery" not in asset, f"{label}: default livery has no editions")
            editions = [asset]
        for edition in editions:
            validate_edition(root, asset, edition, mod_owners)
            if edition["status"] == "available":
                available_mods.add(edition["modFolder"].casefold())
                release_requirements.append((label, effective_requirements(asset, edition)))
    for label, requirements in release_requirements:
        for name in requirements:
            require(name not in mod_owners or name in available_mods,
                    f"{label}: required catalogue pack is not published: {name}")
    return data


def build(root=ROOT):
    root = Path(root)
    data = validate(root, json.loads((root / "catalog.json").read_text()))
    (root / "docs/catalog.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    tracked = [asset for asset in data["assets"] if asset.get("countsTowardProgress", True)]
    available = sum(asset["status"] == "available" for asset in tracked)
    print(f"Catalogue validated: {len(data['groups'])} groups, {len(data['categories'])} categories, "
          f"{available}/{len(tracked)} tracked assets available, {len(data['assets']) - len(tracked)} names awaiting scope audit.")
    return data


if __name__ == "__main__":
    build()
