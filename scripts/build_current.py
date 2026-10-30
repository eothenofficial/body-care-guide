"""Build the approved full guide for Pages; preserve the historical content baseline."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build import build
from scripts.content_model import ContentError, read_json, validate_content, write_json

STAGE = ROOT / '.draft-preview/current'


def current_data():
    config = read_json(ROOT / 'release/current.json')
    source = (ROOT / config['source']).resolve()
    if not source.is_relative_to(ROOT.resolve()) or source.suffix != '.py':
        raise ContentError('Current source must be a project-local Python file')
    spec = importlib.util.spec_from_file_location('approved_current_release', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    book, chapters, sources, registry = module.make_data()
    observed = dict(title=book['title'], content_version=book['content_version'],
                    entry_count=sum(len(c['entries']) for c in chapters),
                    chapter_count=len(chapters), source_count=len(sources),
                    alias_count=len(book.get('entry_aliases', {})))
    for key, value in observed.items():
        if config[key] != value:
            raise ContentError(f'Approved release mismatch: {key}')
    if book['clinical_review_status'] != 'not_clinically_reviewed':
        raise ContentError('Publication cannot change clinical review status')
    validate_content(book, chapters, sources, registry)
    return config, book, chapters, sources, registry


def reset_generated(path: Path, expected: Path):
    """Only reset one explicitly named, project-local generated directory."""
    if path.is_symlink() or path.resolve() != expected.resolve():
        raise ContentError('Unsafe generated directory')
    if not path.resolve().is_relative_to(ROOT.resolve()) or path.resolve() == ROOT.resolve():
        raise ContentError('Generated output must remain inside this project')
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def prepare(stage: Path = STAGE):
    resolved = stage.resolve()
    allowed = [ROOT / '.draft-preview', ROOT / '.test-tmp']
    if not any(resolved.is_relative_to(base.resolve()) and resolved != base.resolve() for base in allowed):
        raise ContentError('Current staging must be below a generated temporary directory')
    config, book, chapters, sources, registry = current_data()
    reset_generated(stage, stage)
    for name, value in [('book', book), ('sources', sources), ('id-registry', registry)]:
        write_json(stage / 'content' / (name + '.json'), value)
    write_json(stage / 'content/config.json', dict(title=config['title'],
        repository_url=config['repository_url'], site_url=config['site_url'], planned_parts=[]))
    for chapter in chapters:
        write_json(stage / 'content/chapters' / (chapter['id'] + '.json'), chapter)
    # Keep the existing online bookmark key; the local-preview namespace is separate.
    shutil.copytree(ROOT / 'web', stage / 'web')
    return config


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Prepare current canonical stage and validate without generating dist')
    args = parser.parse_args(argv)
    config = prepare()
    manifest = build(root=STAGE, check_only=args.check)
    for key in ['title', 'content_version', 'entry_count', 'chapter_count', 'source_count', 'site_url', 'repository_url']:
        if manifest[key] != config[key]:
            raise ContentError('Production manifest mismatch: ' + key)
    if not args.check:
        output = ROOT / 'dist'
        reset_generated(output, ROOT / 'dist')
        shutil.copytree(STAGE / 'dist', output, dirs_exist_ok=True)
    result = dict(mode='check' if args.check else 'build', title=manifest['title'],
                  content_version=manifest['content_version'], entries=manifest['entry_count'],
                  chapters=manifest['chapter_count'], sources=manifest['source_count'],
                  stage='.draft-preview/current', output=None if args.check else 'dist',
                  site_url=manifest['site_url'], clinical_review_status=manifest['clinical_review_status'])
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ContentError, OSError, ValueError) as exc:
        print(f'Current build failed: {exc}', file=sys.stderr)
        raise SystemExit(1)
