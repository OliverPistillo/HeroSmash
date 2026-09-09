"""Detect and install only owner-authorized official Android export components."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[2]
CACHE=ROOT/'.work/downloads/android-v120'
REPORT=ROOT/'.work/reports/v120'
SDK=Path(os.environ['LOCALAPPDATA'])/'Android/Sdk'
TEMPLATES=Path(os.environ['APPDATA'])/'Godot/export_templates/4.7.2.stable'
PACKAGES=['platform-tools','build-tools;35.0.1','platforms;android-35','cmdline-tools;latest','cmake;3.10.2.4988404','ndk;28.1.13356709']
DOWNLOADS=[
 ('commandlinetools-win-15859902_latest.zip','https://dl.google.com/android/repository/commandlinetools-win-15859902_latest.zip','90ae805d20434428bffcb699c290860f19bb5f66a67e6b330067e3de801fb04a'),
 ('Godot_v4.7.2-stable_export_templates.tpz','https://github.com/godotengine/godot-builds/releases/download/4.7.2-stable/Godot_v4.7.2-stable_export_templates.tpz','f298490b8d44d934be425a5a65a51bf15f422428b229a06a6e11d9ffea248011')]


def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def download(item):
    name,url,digest=item;path=CACHE/name
    if path.exists() and sha(path)==digest:return path
    partial=path.with_suffix(path.suffix+'.partial')
    print('DOWNLOAD',name,flush=True)
    with urllib.request.urlopen(url,timeout=90) as response,partial.open('wb') as stream:
        shutil.copyfileobj(response,stream,1024*1024)
    assert sha(partial)==digest,'Official archive digest mismatch: '+name
    partial.replace(path)
    print('VERIFIED',name,flush=True)
    return path


def extract(archive,destination,prefix='',selected=None):
    destination=destination.resolve();destination.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as zipped:
        for member in zipped.infolist():
            if member.is_dir() or not member.filename.startswith(prefix):continue
            name=member.filename[len(prefix):]
            if selected is not None and name not in selected:continue
            target=(destination/name).resolve()
            assert target.is_relative_to(destination),'Unsafe archive member'
            # Never replace a previously existing component silently.
            if target.exists():continue
            target.parent.mkdir(parents=True,exist_ok=True)
            with zipped.open(member) as source,target.open('wb') as sink:shutil.copyfileobj(source,sink)


def properties(path):
    if not path.exists():return None
    return dict(tuple(part.strip() for part in line.split('=',1)) for line in path.read_text(encoding='utf-8').splitlines() if '=' in line and not line.startswith('#'))


def inventory():
    return dict(sdk=str(SDK),java_home=os.environ.get('JAVA_HOME'),templates=str(TEMPLATES),packages={p:properties(SDK/p.replace(';','/')/'source.properties') for p in PACKAGES},template_files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in TEMPLATES.glob('*') if p.is_file()})


def main():
    p=argparse.ArgumentParser();p.add_argument('--install',action='store_true');a=p.parse_args()
    REPORT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(parents=True,exist_ok=True)
    before=inventory()
    if not (REPORT/'android-before.json').exists():(REPORT/'android-before.json').write_text(json.dumps(before,indent=2)+'\n',encoding='utf-8')
    if not a.install:print(json.dumps(before,indent=2));return
    sdkmanager=SDK/'cmdline-tools/latest/bin/sdkmanager.bat'
    needed=[]
    if not sdkmanager.exists():needed.append(DOWNLOADS[0])
    template_names={'version.txt','android_debug.apk','android_release.apk','android_source.zip'}
    if not all((TEMPLATES/name).exists() for name in template_names):needed.append(DOWNLOADS[1])
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(download,needed))
    if not sdkmanager.exists():extract(CACHE/DOWNLOADS[0][0],SDK/'cmdline-tools/latest','cmdline-tools/')
    # sdkmanager resolves installed packages and does not reinstall valid pinned ones.
    absent=[p for p in PACKAGES if not (SDK/p.replace(';','/')/'source.properties').exists()]
    if absent:
        cmd=[str(sdkmanager),'--sdk_root='+str(SDK),'--install',*absent]
        print('INSTALL',absent,flush=True)
        with (REPORT/'sdk-install.log').open('w',encoding='utf-8') as log:
            proc=subprocess.run(cmd,input='y\n'*100,text=True,encoding='utf-8',errors='replace',stdout=log,stderr=subprocess.STDOUT,timeout=3600)
        assert proc.returncode==0,'sdkmanager failed; see .work/reports/v120/sdk-install.log'
    if not all((TEMPLATES/name).exists() for name in template_names):
        extract(CACHE/DOWNLOADS[1][0],TEMPLATES,'templates/',template_names)
    assert (TEMPLATES/'version.txt').read_text().strip()=='4.7.2.stable'
    after=inventory();assert all(after['packages'].values()),'Missing requested package'
    installed=after['packages']
    assert int(installed['platform-tools']['Pkg.Revision'].split('.')[0])>=35
    assert installed['build-tools;35.0.1']['Pkg.Revision']=='35.0.1'
    assert installed['platforms;android-35']['AndroidVersion.ApiLevel']=='35'
    assert installed['ndk;28.1.13356709']['Pkg.Revision']=='28.1.13356709'
    assert installed['cmake;3.10.2.4988404']['Pkg.Path']=='cmake;3.10.2.4988404'
    adb=SDK/'platform-tools/adb.exe'
    devices=subprocess.run([str(adb),'devices','-l'],capture_output=True,text=True,timeout=30)
    after['adb_devices']=devices.stdout;after['adb_stderr']=devices.stderr
    after['status']='installed';after['official_archives']=[dict(name=x[0],url=x[1],sha256=x[2]) for x in DOWNLOADS]
    after['license_scope']='Owner-authorized official packages only; accepted interactively through sdkmanager install stdin'
    (REPORT/'android-installed.json').write_text(json.dumps(after,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(after,indent=2))


if __name__=='__main__':main()
