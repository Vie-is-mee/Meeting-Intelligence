"""Build reviewable static/source ZIPs from allowlists; never include env, results or temp files."""
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    target=ROOT/'dist'
    target.mkdir(exist_ok=True)
    root_files=['README.md','requirements.txt','.env.example','.gitignore','.gitattributes','cli.py','web.py','run_web.cmd','run_demo.cmd']
    files=[ROOT/p for p in root_files]
    for name in ['meeting_intelligence','frontend','samples','datasets','tests','scripts','docs']:
        files.extend(p for p in sorted((ROOT/name).rglob('*')) if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix in {'.py','.js','.cjs','.css','.html','.json','.md','.txt'})
    secret_pattern=re.compile(rb'(?:gsk_[A-Za-z0-9]{24,}|sk-proj-[A-Za-z0-9_-]{24,})')
    hashes={}
    for p in files:
        content=p.read_bytes()
        if secret_pattern.search(content): raise SystemExit('Potential key in allowlisted file: '+str(p.relative_to(ROOT)))
        hashes[p.relative_to(ROOT).as_posix()]=hashlib.sha256(content).hexdigest()
    static={'index.html':ROOT/'frontend/index.html','app.js':ROOT/'frontend/app.js',
            'review.js':ROOT/'frontend/review.js',
            'review.css':ROOT/'frontend/review.css',
            'workspace.css':ROOT/'frontend/workspace.css',
            'styles.css':ROOT/'frontend/styles.css','demo-data.json':ROOT/'frontend/demo-data.json',
            'README.md':ROOT/'docs/STATIC_DEMO.md'}
    with zipfile.ZipFile(target/'meeting-intelligence-demo-static.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for name,p in static.items(): archive.write(p,name)
    with zipfile.ZipFile(target/'meeting-intelligence-mission2-source.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for p in files: archive.write(p,p.relative_to(ROOT).as_posix())
    info={'purpose':'Local/static demo packages; not yet deployed or published.',
          'files_sha256':hashes,'archives':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in target.glob('*.zip')}}
    (target/'BUILD_INFO.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for name in info['archives']:
        with zipfile.ZipFile(target/name) as archive:
            assert not any(n=='.env' or '/tmp/' in n or n.startswith('results/') or '__pycache__' in n for n in archive.namelist())
            assert archive.testzip() is None
        print(name, (target/name).stat().st_size,'bytes')


if __name__=='__main__': main()
