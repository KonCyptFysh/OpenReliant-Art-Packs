# Maintaining this mod

Git records local versions of files. GitHub hosts the repository online, tracks issues and provides player downloads. A commit is a named snapshot; pushing sends commits to GitHub. A tag marks an exact version. A Release attaches installable files and release notes to that version.

## First public beta

1. Finish the current editing passes and make one frozen copy of the deployed assets. Keep the working originals where they are. Use the mod root directly; nested authoring folders do not load in OpenReliant.
2. Update the asset inventory, credits and chosen licence terms. Keep font and engine notices with their files. Do not assign an engine licence to artwork by assumption.
3. Install Git LFS before adding the binary art files: this repository's `.gitattributes` is already prepared for it. LFS keeps successive large images out of ordinary Git history. Player downloads must contain real files, never LFS pointer text.
4. Validate on the exact OpenReliant release and record results in `validation.json`. Populate `asset-manifest.json` with each relative `mods/<folder>/<file>` path, byte size and SHA-256. Pin its hash in both `release.json` and `validation.json`.
5. Set `release.json` to `ready-for-packaging` only after the tests pass. Run `python3 tools/package_mod.py`. Upload the resulting ZIP and SHA-256 file as Release attachments.
6. Set the Git author name and preferred public or GitHub no-reply email, create the first commit and create an empty GitHub repository. Push the prepared repository to it. Keep any token out of files and chat.
7. Import only issue drafts whose matching record in `tracking/issues.json` has `status: open`, using the labels and milestones in `tracking/github-setup.json`. Keep resolved historical records closed; do not create them as open issues. Preserve each stable tracking ID in the issue so the import can be checked for duplicates. Replace the local references in KNOWN_ISSUES.md with issue links once those exist.
8. Tag the first candidate `v0.1.0-beta.1`, create a draft Release, attach the ZIP and checksum, and confirm that a clean installation works. Mark the published Release as a pre-release. Start with the HUD; release the fighters separately when ready.

## Routine bug handling

Acknowledge the report, check for duplicates and ask only for missing reproduction details. Use `bug` for broken behaviour, `unfinished-art` for an acknowledged visual gap, `planned` for future additions, `compatibility` for version conflicts, and `needs-review` when the cause is unclear. A planned emissive update is not automatically a bug.

Use milestones for release goals: first beta, artwork completion and later feature updates. Do not give every future idea a release date. If a report also happens with this mod disabled, record that evidence before routing it to the engine project.

For a fix, use a short branch such as `fix/radar-fringe`, make a focused commit, test the affected behaviour and add an Unreleased changelog entry. A pull request lets the exact change be reviewed before merging. Record which release contains the fix when closing the issue. Do not replace an existing release ZIP silently; publish a new version.

## Package-tool checks

`python3 tools/test_package_mod.py` runs synthetic packaging checks. These test archive integrity, real-file inclusion, deterministic output, stale manifests, missing files, path collisions and LFS pointers. They do not test the HUD or fighters in game.

## Large files and downloads

Keep editable art and runtime binaries in Git LFS when added. Keep generated ZIP/HOG files in GitHub Releases, with `dist/` ignored by Git. Upload release ZIPs containing the real assets; GitHub's automatic source archives are not the player installation package. Keep screenshots small and relevant. The fighter pack currently contains duplicate texture aliases that the engine may need; do not remove them to save space without checking the model references.

## References

- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
- [GitHub large-file guidance](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)
- [Creating and tracking issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue)
- [OpenReliant v0.7.0 modding guide](https://github.com/OpenReliant/openreliant/blob/v0.7.0/docs/guide/modding.md)
