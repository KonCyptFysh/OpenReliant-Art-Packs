#!/usr/bin/env python3
"""Validate a frozen mod tree and build a reproducible player download.

Run from any directory. Uses only Python's standard library. It never reads
the live game, changes installed assets, uploads files, or launches the game.
"""
import argparse
import configparser
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def engine_version(value):
    if not re.fullmatch(r"[0-9]+\.[0-9]+(?:\.[0-9]+)?", value):
        raise ValueError("Invalid minimum OpenReliant version: " + value)
    parts = tuple(int(p) for p in value.split("."))
    return parts + (0,) * (3 - len(parts))


def validate(root):
    config = json.loads((root / "release.json").read_text())
    if config["status"] != "ready-for-packaging":
        raise ValueError("Release is on hold: " + config["hold_reason"])
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*", config["package_name"]):
        raise ValueError("Unsafe package name")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[a-z0-9.-]+)?", config["version"]):
        raise ValueError("Invalid release version")
    manifest_path = root / "asset-manifest.json"
    records = json.loads(manifest_path.read_text())
    if not records:
        raise ValueError("No frozen assets in asset-manifest.json")
    if config.get("asset_manifest_sha256") != digest(manifest_path):
        raise ValueError("Release is not pinned to this asset manifest")
    report_path = root / "validation.json"
    report = json.loads(report_path.read_text())
    if report.get("status") != "passed":
        raise ValueError("Runtime validation has not passed")
    if report.get("asset_manifest_sha256") != digest(manifest_path):
        raise ValueError("Runtime evidence describes different assets")
    if not report.get("engine_build") or not report.get("tested_platforms") or not report.get("checks"):
        raise ValueError("Runtime evidence needs an exact engine build, platforms and checks")
    expected = {}
    for record in records:
        name = record["path"]
        parts = name.split("/")
        if len(parts) != 3 or parts[0] != "mods" or any(p in ("", ".", "..") for p in parts):
            raise ValueError("Expected mods/<mod-name>/<flat-file>: " + name)
        if "\\" in name or any(ord(c) < 32 or ord(c) > 126 for c in name):
            raise ValueError("Nonportable asset name: " + name)
        if name.casefold() in expected:
            raise ValueError("Case-insensitive path collision: " + name)
        path = root / name
        if any(parent.is_symlink() for parent in (path, path.parent, path.parent.parent)):
            raise ValueError("Assets must be copies, not symlinks: " + name)
        if not path.is_file():
            raise ValueError("Missing asset: " + name)
        if path.stat().st_size != record["bytes"] or digest(path) != record["sha256"]:
            raise ValueError("Asset changed since freeze: " + name)
        with path.open("rb") as stream:
            if stream.read(80).startswith(b"version https://git-lfs.github.com/spec/v1"):
                raise ValueError("Git LFS pointer instead of real asset: " + name)
        expected[name.casefold()] = path
    # A g/r loadout copy must not repeat a shipped canonical material image.
    for name, path in expected.items():
        if path.suffix.lower() not in {".png", ".dds", ".ktx2"} or path.name[0].lower() not in "gr":
            continue
        original = expected.get((path.parent / path.name[1:]).relative_to(root).as_posix().casefold())
        if original is not None and digest(path) == digest(original):
            raise ValueError("Redundant loadout colour variant: " + path.relative_to(root).as_posix())
    actual = [p for p in (root / "mods").rglob("*") if p.is_file() or p.is_symlink()]
    if {p.relative_to(root).as_posix().casefold() for p in actual} != set(expected):
        raise ValueError("Unmanifested files in mods/")
    mod_names = sorted({p.parent.name for p in expected.values()})
    if mod_names != sorted(config["mod_folders"]):
        raise ValueError("Unexpected mod folder list")
    for name in mod_names:
        manifest = root / "mods" / name / "mod.ini"
        ini = configparser.ConfigParser(interpolation=None)
        ini.read(manifest)
        if not ini.has_section("Mod") or not ini.get("Mod", "Name", fallback=""):
            raise ValueError("Missing [Mod] Name in " + str(manifest))
        if engine_version(ini.get("Mod", "OpenReliant", fallback="")) > engine_version(config["minimum_openreliant"]):
            raise ValueError("Mod requires a newer OpenReliant than the package baseline: " + str(manifest))
    for name in config["include_documents"]:
        path = root / name
        if Path(name).is_absolute() or ".." in Path(name).parts or path.is_symlink() or not path.is_file():
            raise ValueError("Missing or unsafe release document: " + name)
    return config, sorted(expected.values())


def build(root):
    config, assets = validate(root)
    destination = root / "dist" / (config["package_name"] + "-" + config["version"] + ".zip")
    destination.parent.mkdir(exist_ok=True)
    temporary = destination.with_suffix(".zip.partial")
    files = assets + [root / p for p in config["include_documents"]]
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(set(files)):
            member = zipfile.ZipInfo(path.relative_to(root).as_posix(), (2026, 1, 1, 0, 0, 0))
            member.compress_type = zipfile.ZIP_DEFLATED
            member.external_attr = (0o100755 if path.stat().st_mode & 0o111 else 0o100644) << 16
            archive.writestr(member, path.read_bytes())
    with zipfile.ZipFile(temporary) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError("ZIP integrity failure: " + bad)
        for path in assets:
            if hashlib.sha256(archive.read(path.relative_to(root).as_posix())).hexdigest() != digest(path):
                raise ValueError("Packaged asset differs: " + str(path))
    temporary.replace(destination)
    destination.with_suffix(".zip.sha256").write_text(digest(destination) + "  " + destination.name + "\n")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate without creating a ZIP")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    try:
        if args.check:
            _, files = validate(args.root)
            print(f"Validated {len(files)} frozen files")
        else:
            print(build(args.root))
    except (OSError, ValueError, KeyError, configparser.Error) as error:
        sys.exit(str(error))
