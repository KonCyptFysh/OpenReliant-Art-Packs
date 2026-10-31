import unittest
import contextlib
import io
import os
from pathlib import Path
import subprocess
import tempfile
from release_policy import private_reason, check

class PublicationBoundary(unittest.TestCase):
    def test_rejects_masters_even_outside_source_folder(self):
        for name in ['Alliance Fighters/Coyote/source/ship.blend', 'docs/assets/master.psd',
                     'Alliance Fighters/Coyote/mods/30-coyote/ship.blend',
                     'Alliance Fighters/Coyote/backup.blend1',
                     'HUD/Recommissioned/source/portraits/frame0001.png']:
            with self.subTest(name=name): self.assertIsNotNone(private_reason(name))

    def test_rejects_working_snapshots_and_unpublished_binary_locations(self):
        for name in ['Alliance Capital Ships/Reliant/dev/mission.dte',
                     'Weapons/Ordnance/review/preview.png',
                     'HUD/Recommissioned/tracking/history/old.png',
                     'Alliance Fighters/Coyote/source-manifest.json',
                     'tracking/artwork.png', 'backup/archive.zip']:
            with self.subTest(name=name): self.assertIsNotNone(private_reason(name))

    def test_preserves_runtime_materials_and_release_evidence(self):
        for name in ['Alliance Fighters/Coyote/mods/30-coyote/hull_normal.png',
                     'Alliance Capital Ships/Reliant/mods/121-reliant/reliant_power.luau',
                     'HUD/Recommissioned/mods/50-hud/portrait.FM8',
                     'docs/models/coyote.glb', 'docs/assets/coyote/gallery.webp',
                     'Alliance Fighters/Coyote/asset-manifest.json',
                     'tracking/gallery-standard-captures.json',
                     'tools/package_mod.py', '.github/workflows/release-only.yml']:
            with self.subTest(name=name): self.assertIsNone(private_reason(name))

    def test_old_clone_cannot_restore_sources_hidden_in_ancestors(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as temporary:
            try:
                os.chdir(temporary)
                def git(*args):
                    subprocess.run(['git', '-c', 'user.name=Policy test',
                                    '-c', 'user.email=test@example.invalid', *args],
                                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                git('init', '-q')
                Path('README.md').write_text('Release files')
                git('add', 'README.md'); git('commit', '-qm', 'Clean release')
                with contextlib.redirect_stdout(io.StringIO()): check('HEAD', history=True)
                Path('source').mkdir(); Path('source/master.blend').write_text('private master')
                git('add', 'source'); git('commit', '-qm', 'Old source upload')
                git('rm', 'source/master.blend'); git('commit', '-qm', 'Only delete current source')
                with contextlib.redirect_stdout(io.StringIO()): check('HEAD')
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(ValueError):
                    check('HEAD', history=True)
            finally:
                os.chdir(previous)

if __name__ == '__main__': unittest.main()
