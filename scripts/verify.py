#!/usr/bin/env python3
"""Caldea M1 산출물과 링크·시딩 보존 계약 검사 (표준 라이브러리만 사용)."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DELIVERABLES = [
    'README.ko.md', 'docs/00-research.md', 'docs/ROADMAP.md',
    'docs/install.md', 'docs/workflow.md', 'templates/AGENTS.md',
    'skills/milestone-loop/SKILL.md', 'install.sh',
]


def prose(text):
    return re.sub(r'(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1[^\n]*$', '', text)


def anchors(text):
    result, counts = set(), {}
    for line in text.splitlines():
        match = re.match(r'^#{1,6}\s+(.+)', line)
        if match:
            value = re.sub(r'<[^>]+>', '', match[1]).strip().lower()
            value = re.sub(r'[^\w\-\s]', '', value).replace(' ', '-')
            suffix = counts.get(value, 0)
            counts[value] = suffix + 1
            result.add(value if not suffix else f'{value}-{suffix}')
    result.update(re.findall(r'(?:id|name)=["\']([^"\']+)', text))
    return result


def links(text):
    text = prose(text)
    # 인라인 코드의 예시 링크는 렌더링 링크가 아니다.
    text = re.sub(r'`[^`\n]+`', '', text)
    inline = re.findall(r'!?\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+["\'][^\n]*?["\'])?\)', text)
    definitions = dict(re.findall(r'^\s*\[([^\]]+)\]:\s*(\S+)', text, re.M))
    targets = inline + list(definitions.values())
    for label, key in re.findall(r'\[([^\]\n]+)\]\[([^\]\n]*)\]', text):
        actual = key or label
        if actual not in definitions:
            raise ValueError(f'미정의 reference link: {actual}')
    return [target.strip('<>') for target in targets]


def check_links(path, base=None):
    count = 0
    for target in links(path.read_text(encoding='utf-8')):
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc:
            continue
        if parsed.path.startswith('/'):
            raise ValueError(f'배포 문서에 절대 파일 링크 금지: {path}: {target}')
        destination = ((base or path.parent) / unquote(parsed.path)).resolve() if parsed.path else path
        if not destination.exists():
            raise ValueError(f'깨진 상대 링크: {path.relative_to(ROOT)} → {target}')
        if parsed.fragment and destination.suffix == '.md':
            if unquote(parsed.fragment) not in anchors(destination.read_text(encoding='utf-8')):
                raise ValueError(f'깨진 앵커: {path.relative_to(ROOT)} → {target}')
        count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-links', action='store_true', help='시딩 링크를 원본 경로 기준 추가 검사')
    parser.add_argument('--base', default='d5538a3', help='커밋된 변경의 공백 검사 기준 revision (기본: d5538a3)')
    args = parser.parse_args()
    errors = []
    for name in DELIVERABLES:
        path = ROOT / name
        if not path.is_file() or len(path.read_text(encoding='utf-8').strip()) < 100:
            errors.append(f'산출물 누락 또는 100자 미만: {name}')
    manifest = json.loads((ROOT / 'scripts/source-manifest.json').read_text())
    for item in manifest['seeded']:
        path = ROOT / item['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            errors.append(f'시딩 변경: {item["path"]}')
    count = 0
    for path in sorted(ROOT.rglob('*.md')):
        if '.git' in path.parts or 'references' == path.relative_to(ROOT).parts[0]:
            continue
        try:
            count += check_links(path)
        except ValueError as error:
            errors.append(str(error))
    # 이 스킬은 YAML의 JSON-compatible scalar 부분집합만 사용한다.
    skill = (ROOT / 'skills/milestone-loop/SKILL.md').read_text()
    front = re.match(r'\A---\nname: ([a-z0-9-]+)\ndescription: ("[^\n]+")\n---\n', skill)
    try:
        if not front or front[1] != 'milestone-loop' or not json.loads(front[2]):
            raise ValueError('유효한 name/description YAML frontmatter 없음')
    except (ValueError, TypeError) as error:
        errors.append(str(error))
    if subprocess.run(['bash', '-n', str(ROOT / 'install.sh')], cwd=ROOT).returncode:
        errors.append('bash -n 실패')
    if subprocess.run(['git', 'diff', '--check'], cwd=ROOT).returncode:
        errors.append('git diff --check 실패')
    base = subprocess.run(
        ['git', 'rev-parse', '--verify', '--end-of-options', f'{args.base}^{{commit}}'],
        cwd=ROOT, capture_output=True, text=True,
    )
    if base.returncode:
        errors.append(f'유효하지 않은 기준 revision: {args.base}')
    elif subprocess.run(['git', 'diff', f'{base.stdout.strip()}..HEAD', '--check', '--'], cwd=ROOT).returncode:
        errors.append(f'git diff {args.base}..HEAD --check 실패')
    source_count = 0
    if args.source_links:
        for item in manifest['seeded']:
            if item.get('original_path'):
                original = Path(item['original_path'])
                if not original.is_file():
                    errors.append(f'원본 경로 없음: {original}')
                    continue
                try:
                    source_count += check_links(ROOT / item['path'], base=original.parent)
                except ValueError as error:
                    errors.append(str(error))
        # 실제 읽은 로컬 자료가 기록 시점과 같은지도 확인한다.
        for item in manifest['local_sources']:
            path = Path(item['path'])
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
                errors.append(f'로컬 자료 누락/변경: {path}')
    for error in errors:
        print('FAIL:', error)
    if errors:
        return 1
    print(f'PASS: 필수 산출물 8개(각 100자 이상), 새 문서 상대 링크 {count}개, YAML frontmatter, Bash 구문, diff 공백, 시딩 4개 SHA-256')
    if args.source_links:
        print(f'PASS: 시딩 원본 경로 기준 링크 {source_count}개, 로컬 필독 자료 9개 hash 일치')
    else:
        print('시딩 원본 경로 링크는 --source-links로 별도 검증 (D001).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
