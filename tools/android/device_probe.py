"""Physical-only adb discovery and bounded QA deployment/profile capture."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[2]
ADB=Path(os.environ['LOCALAPPDATA'])/'Android/Sdk/platform-tools/adb.exe'


def adb(*args):
    p=subprocess.run([str(ADB),*map(str,args)],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60)
    return dict(code=p.returncode,stdout=p.stdout,stderr=p.stderr)


def main():
    p=argparse.ArgumentParser();p.add_argument('--apk',type=Path,default=ROOT/'.work/builds/hero-smash-v120-debug.apk');p.add_argument('--deploy',action='store_true');p.add_argument('--seconds',type=int,default=120);a=p.parse_args()
    output=ROOT/'.work/reports/v120/device';output.mkdir(parents=True,exist_ok=True)
    discovery=adb('devices','-l');physical=[]
    for line in discovery['stdout'].splitlines()[1:]:
        fields=line.split()
        if len(fields)>1 and fields[1]=='device' and not fields[0].startswith('emulator-'):
            serial=fields[0]
            if adb('-s',serial,'shell','getprop','ro.kernel.qemu')['stdout'].strip()!='1':physical.append(serial)
    report=dict(discovery=discovery,physical_count=len(physical),status='BLOCKED',reason='No authorized physical Android device connected',measurements=None)
    if physical:
        serial=physical[0];report.update(status='DETECTED',reason='',selected_serial=serial)
        commands={'properties':['getprop'],'display':['dumpsys','display'],'resolution':['wm','size'],'memory':['cat','/proc/meminfo'],'gpu':['dumpsys','SurfaceFlinger']}
        report['metadata']={name:adb('-s',serial,'shell',*command) for name,command in commands.items()}
        if a.deploy:
            assert a.apk.is_file()
            installed=adb('-s',serial,'install','-r',str(a.apk.resolve()));assert installed['code']==0,installed
            report['install']=installed
            report['launch']=adb('-s',serial,'shell','am','start','-W','-n','org.herosmash.qa/com.godot.game.GodotApp')
            assert report['launch']['code']==0 and 'Error' not in report['launch']['stdout'],report['launch']
            samples=[];start=time.monotonic()
            while time.monotonic()-start<a.seconds:
                sample=dict(elapsed_s=time.monotonic()-start,memory=adb('-s',serial,'shell','dumpsys','meminfo','org.herosmash.qa'),thermal=adb('-s',serial,'shell','dumpsys','thermalservice'))
                samples.append(sample);print('DEVICE_SAMPLE',round(sample['elapsed_s']),flush=True);time.sleep(10)
            logs=adb('-s',serial,'logcat','-d','-v','threadtime')
            (output/'logcat.txt').write_text(logs['stdout'],encoding='utf-8')
            report.update(status='CAPTURED_REQUIRES_REVIEW',duration_seconds=time.monotonic()-start,measurements=samples,notes='Review actual SLICE_SAMPLE logs/crashes. Missing GPU/vendor counters remain unavailable, never zero.')
    (output/'device.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ('metadata','measurements')},indent=2))


if __name__=='__main__':main()
