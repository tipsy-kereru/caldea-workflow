#!/usr/bin/env python3
"""실제 홈을 변경하지 않는 임시 프로젝트 기반 설치 계약 검증."""
from pathlib import Path
import os
import shutil
import stat
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
START = b'<!-- caldea-workflow:start -->'
END = b'<!-- caldea-workflow:end -->'


class InstallContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.path.realpath(tempfile.gettempdir()))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / '한글 project'
        self.project.mkdir()
        self.skills = self.root / 'agent skills'
        self.agents = self.project / 'AGENTS.md'
        self.skill = self.skills / 'milestone-loop/SKILL.md'

    def run_install(self, *extra, code=0, target='agents', project=None, skills=None):
        process = subprocess.run(
            ['bash', str(ROOT / 'install.sh'), '--project', str(project or self.project),
             '--target', target, '--skills-dir', str(skills or self.skills), *extra],
            capture_output=True, text=True, cwd=self.root,
        )
        self.assertEqual(process.returncode, code, process.stdout + process.stderr)
        return process

    def snapshot(self):
        return {str(p.relative_to(self.root)): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.root.rglob('*') if p.is_file()}

    def test_fresh_install_and_readonly_check(self):
        self.run_install('--check', code=1)
        self.assertFalse(self.skills.exists())
        self.assertFalse(self.agents.exists())
        self.run_install()
        self.assertEqual(self.skill.read_bytes(), (ROOT / 'skills/milestone-loop/SKILL.md').read_bytes())
        before = self.snapshot()
        self.run_install('--check')
        self.assertEqual(before, self.snapshot())

    def test_existing_utf8_without_newline_preserved_and_backed_up(self):
        original = '# 기존 규칙\n질문은 Spokenly로. $() `literal`'.encode()
        self.agents.write_bytes(original)
        self.agents.chmod(0o640)
        self.run_install()
        self.assertTrue(self.agents.read_bytes().startswith(original + b'\n\n'))
        backups = list(self.project.glob('AGENTS.md.bak-*'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        self.assertEqual(stat.S_IMODE(self.agents.stat().st_mode), 0o640)

    def test_repeated_install_does_not_touch_mtime_or_create_backup(self):
        self.agents.write_text('사용자 규칙\n')
        self.run_install()
        before = self.snapshot()
        self.run_install()
        self.run_install('--check')
        self.assertEqual(before, self.snapshot())
        self.assertEqual(self.agents.read_bytes().count(START), 1)

    def test_replace_block_preserves_prefix_suffix_and_other_markers(self):
        prefix = b'# user\r\n<!-- ai-memory:start -->\r\nkeep\r\n<!-- ai-memory:end -->\r\n'
        suffix = '\r\n## 뒤쪽 규칙\r\n보존'.encode()
        original = prefix + START + b'\r\nold\r\n' + END + b'\r\n' + suffix
        self.agents.write_bytes(original)
        self.run_install()
        self.assertTrue(self.agents.read_bytes().startswith(prefix))
        self.assertTrue(self.agents.read_bytes().endswith(suffix))
        self.assertNotIn(b'\nold\r\n', self.agents.read_bytes())
        self.run_install('--check')

    def test_drift_check_never_repairs_and_update_backs_up(self):
        self.run_install()
        changed = self.skill.read_bytes() + b'\nlocal change\n'
        self.skill.write_bytes(changed)
        self.agents.write_bytes(self.agents.read_bytes().replace('최대 3라운드'.encode(), '최대 9라운드'.encode()))
        before = self.snapshot()
        self.run_install('--check', code=1)
        self.assertEqual(before, self.snapshot())
        self.run_install()
        self.run_install('--check')
        self.assertEqual(list(self.skill.parent.glob('SKILL.md.bak-*'))[0].read_bytes(), changed)

    def test_malformed_markers_fail_before_any_write(self):
        cases = [START, END, END + b'\n' + START,
                 START + b'\nx\n' + END + b'\n' + START + b'\ny\n' + END,
                 b'inline ' + START + b'\nx\n' + END]
        for data in cases:
            with self.subTest(data=data):
                self.agents.write_bytes(data)
                before = self.snapshot()
                self.run_install(code=2)
                self.run_install('--check', code=2)
                self.assertEqual(before, self.snapshot())
                self.assertFalse(self.skills.exists())

    def test_unmanaged_skill_collision_is_preserved(self):
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text('사용자의 다른 milestone-loop 스킬')
        before = self.snapshot()
        self.run_install(code=2)
        self.assertEqual(before, self.snapshot())
        self.assertFalse(self.agents.exists())

    def test_symlink_agents_and_skill_parent_are_refused(self):
        other = self.root / 'other.md'
        other.write_text('보존')
        self.agents.symlink_to(other)
        self.run_install(code=2)
        self.assertEqual(other.read_text(), '보존')
        self.agents.unlink()
        self.skills.mkdir()
        actual = self.root / 'actual'
        actual.mkdir()
        (self.skills / 'milestone-loop').symlink_to(actual, target_is_directory=True)
        self.run_install(code=2)
        self.assertEqual(list(actual.iterdir()), [])
        self.assertFalse(self.agents.exists())

    def test_claude_and_agents_can_coexist(self):
        self.run_install()
        first = self.agents.read_bytes()
        claude_root = self.root / '.claude/skills'
        self.run_install(target='claude', skills=claude_root)
        self.assertTrue((claude_root / 'milestone-loop/SKILL.md').is_file())
        self.assertEqual(first, self.agents.read_bytes())
        self.assertEqual(first.count(START), 1)
        self.run_install('--check', target='claude', skills=claude_root)

    def test_invalid_arguments_and_missing_project(self):
        self.run_install('--unknown', code=2)
        self.run_install(target='invalid', code=2)
        self.run_install(project=self.root / 'missing', code=2)
        self.assertEqual(self.snapshot(), {})

    def test_shell_metacharacters_in_paths_remain_literal(self):
        path = self.root / 'project $(touch EXPLOIT) `touch EXPLOIT2`'
        path.mkdir()
        self.run_install(project=path)
        self.assertTrue((path / 'AGENTS.md').is_file())
        self.assertFalse((self.root / 'EXPLOIT').exists())
        self.assertFalse((self.root / 'EXPLOIT2').exists())

    def test_lock_refuses_concurrent_install_without_writes(self):
        (self.project / '.caldea-install.lock').mkdir()
        self.run_install(code=2)
        self.assertFalse(self.skills.exists())
        self.assertFalse(self.agents.exists())

    def test_non_file_agents_is_refused_before_skill_copy(self):
        self.agents.mkdir()
        self.run_install(code=2)
        self.assertFalse(self.skills.exists())

    def test_existing_skill_sibling_is_preserved(self):
        self.run_install()
        sibling = self.skill.parent / 'user-notes.txt'
        sibling.write_text('추가 파일 보존')
        self.skill.write_bytes(self.skill.read_bytes() + b'\ndrift\n')
        self.run_install()
        self.assertEqual(sibling.read_text(), '추가 파일 보존')

    def test_mixed_package_versions_fail_before_writes(self):
        package = self.root / 'mixed package'
        source = package / 'skills/milestone-loop/SKILL.md'
        source.parent.mkdir(parents=True)
        shutil.copy2(ROOT / 'install.sh', package / 'install.sh')
        # 본문에 같은 metadata가 있어도 frontmatter의 버전 불일치를 숨길 수 없다.
        (package / 'VERSION').write_text('999.0.0\n')
        source.write_bytes((ROOT / 'skills/milestone-loop/SKILL.md').read_bytes() +
                           b'\nmetadata: {"version": "999.0.0"}\n')
        before = self.snapshot()
        for extra in ([], ['--check']):
            process = subprocess.run(
                ['bash', str(package / 'install.sh'), '--project', str(self.project),
                 '--skills-dir', str(self.skills), *extra],
                capture_output=True, text=True,
            )
            self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
            self.assertEqual(before, self.snapshot())
            self.assertFalse(self.skills.exists())
            self.assertFalse(self.agents.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
