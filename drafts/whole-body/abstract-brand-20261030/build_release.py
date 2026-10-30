"""Retain the edited book; restore the established visual scale and compact home."""
import copy,hashlib,importlib.util,json,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
TARGET=ROOT/'.draft-preview/abstract-brand-20261030'
sys.path.insert(0,str(ROOT))
from scripts.build import build
from scripts.content_model import read_json,write_json,validate_content

def previous():
    spec=importlib.util.spec_from_file_location('visual_previous',HERE.parent/'editorial-readability-20261030/build_release.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def make_data():
    module=previous();module.verify_reviews()
    book,chapters,sources,registry=module.make_data()
    old=copy.deepcopy(book['home_content']);home=copy.deepcopy(old)
    home.update(read_json(HERE/'home-copy.json'))
    home['reader_guide']=home['reader_guide'].replace('字号和行距可在“阅读设置”调整，有用的建议可收藏，并导出备份。','有用的建议可收藏，并导出备份。')
    book.update(content_version='2026.10.30-7',home_content=home)
    for key in ['headline','headline_end','lead','reader_guide']:
        book['front_matter']=book['front_matter'].replace(old[key],home[key])
    registry['edition']=book['content_version']
    validate_content(book,chapters,sources,registry)
    return book,chapters,sources,registry

def main():
    before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'content').rglob('*.json'))}
    book,chapters,sources,registry=make_data()
    config=read_json(ROOT/'content/config.json')
    for name,value in [('book',book),('sources',sources),('id-registry',registry),('config',dict(title=book['title'],repository_url=config['repository_url'],site_url='',planned_parts=[]))]:write_json(TARGET/'content'/(name+'.json'),value)
    for chapter in chapters:write_json(TARGET/'content/chapters'/(chapter['id']+'.json'),chapter)
    shutil.copytree(ROOT/'web',TARGET/'web',dirs_exist_ok=True)
    js=TARGET/'web/app.js';js.write_text(js.read_text(encoding='utf-8').replace("'body-care-guide:bookmarks:v1'","'body-care-guide:whole-body:bookmarks:v1'"),encoding='utf-8')
    build(root=TARGET)
    after={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'content').rglob('*.json'))}
    if before!=after:raise ValueError('Public baseline changed')
    report=dict(content_version=book['content_version'],editorial_preview=False,independent_editorial_review_complete=True,summary_min=60,summary_max=140,entries=sum(len(c['entries']) for c in chapters),merged_entries=len(book['entry_aliases']),sources=len(sources),doi_sources=sum(bool(s.get('doi')) for s in sources),chapters={c['id']:len(c['entries']) for c in chapters},canonical_fingerprints=before,clinical_review_status='not_clinically_reviewed',output=str(TARGET/'dist'),visual_baseline='2026.10.30-4',reading_settings=False)
    write_json(HERE/'build-report.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='canonical_fingerprints'},ensure_ascii=False))

if __name__=='__main__':main()
