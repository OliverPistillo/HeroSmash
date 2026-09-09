"""Reproducible Android QA staging/export, never alters production main scene.

Requires already installed official 4.7.2 templates/SDK and Java17. No downloads.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]


def run(command,log,env):
    result=subprocess.run([str(x) for x in command],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=600)
    output=result.stdout+result.stderr;log.write_text(output,encoding='utf-8')
    assert result.returncode==0 and 'SCRIPT ERROR:' not in output and '\nERROR:' not in output,output[-6000:]
    return output


def main():
    p=argparse.ArgumentParser();p.add_argument('--godot',type=Path,required=True);p.add_argument('--output',type=Path,default=ROOT/'.work/builds/hero-smash-v120-debug.apk');a=p.parse_args()
    godot=a.godot.resolve();sdk=Path(os.environ['LOCALAPPDATA'])/'Android/Sdk';java=Path(os.environ['JAVA_HOME'])
    assert (sdk/'build-tools/35.0.1/apksigner.bat').exists()
    report=ROOT/'.work/reports/v120';report.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='android-qa-',dir=ROOT/'.work'))
    shutil.copytree(ROOT/'game',staging/'game',ignore=shutil.ignore_patterns('.godot'),dirs_exist_ok=True)
    project=staging/'game/project.godot'
    project.write_text(project.read_text().replace('res://scenes/app/bootstrap.tscn','res://scenes/qa/two_fighter_slice.tscn').replace('[application]','[application]\nconfig/icon="res://assets/qa_icon.svg"').replace('[rendering]','[rendering]\ntextures/vram_compression/import_etc2_astc=true'),encoding='utf-8')
    # Isolated editor configuration prevents hidden machine preferences from affecting export.
    appdata=staging/'config';editor=appdata/'Godot';editor.mkdir(parents=True)
    templates=Path(os.environ['APPDATA'])/'Godot/export_templates/4.7.2.stable'
    target=editor/'export_templates/4.7.2.stable';target.mkdir(parents=True)
    for name in ('version.txt','android_debug.apk'):
        shutil.copy2(templates/name,target/name)
    key=ROOT/'.work/android-debug.keystore'
    if not key.exists():
        run([java/'bin/keytool.exe','-genkeypair','-keystore',key,'-storepass','android','-alias','androiddebugkey','-keypass','android','-dname','CN=Android Debug,O=Android,C=US','-keyalg','RSA','-keysize','2048','-validity','10000'],report/'debug-key.log',os.environ.copy())
    settings='[gd_resource type="EditorSettings" format=3]\n\n[resource]\n'
    for name,value in {'export/android/android_sdk_path':sdk,'export/android/java_sdk_path':java,'export/android/debug_keystore':key,'export/android/debug_keystore_user':'androiddebugkey','export/android/debug_keystore_pass':'android'}.items():
        settings+=name+'='+json.dumps(str(value).replace('\\','/'))+'\n'
    (editor/'editor_settings-4.7.tres').write_text(settings,encoding='utf-8')
    env=os.environ.copy();env['APPDATA']=str(appdata);env['ANDROID_HOME']=str(sdk)
    run([godot,'--headless','--path',staging/'game','--editor','--import'],report/'android-import.log',env)
    output=a.output.resolve();output.parent.mkdir(parents=True,exist_ok=True)
    command=[godot,'--headless','--path',staging/'game','--export-debug','Android QA Debug',output]
    run(command,report/'android-export.log',env)
    assert output.is_file()
    signer=run([sdk/'build-tools/35.0.1/apksigner.bat','verify','--verbose',output],report/'apk-signature.log',env)
    metadata=run([sdk/'cmdline-tools/latest/bin/apkanalyzer.bat','manifest','print',output],report/'apk-manifest.xml',env)
    manifest=ET.fromstring(metadata);ns='{http://schemas.android.com/apk/res/android}'
    assert manifest.attrib['package']=='org.herosmash.qa'
    activity=manifest.find('application/activity')
    assert activity is not None and activity.attrib.get(ns+'screenOrientation') in ('0','landscape','6','sensorLandscape')
    with zipfile.ZipFile(output) as apk:
        assert 'AndroidManifest.xml' in apk.namelist() and 'lib/arm64-v8a/libgodot_android.so' in apk.namelist()
    result=dict(status='pass',apk=str(output),bytes=output.stat().st_size,sha256=hashlib.file_digest(output.open('rb'),'sha256').hexdigest(),command=[str(x) for x in command],staging=str(staging),signature_verified=True,package='org.herosmash.qa',physical_device='not asserted',reproducibility='Repeatable debug build from tracked preset/source; debug signature/container metadata may differ',main_scene='res://scenes/qa/two_fighter_slice.tscn')
    (report/'android-export.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
