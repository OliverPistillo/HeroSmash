"""Validate Godot MJPEG AVI and extract unmodified JPEG frames for review."""
from pathlib import Path
import argparse
import hashlib
import json
import struct


def inspect(path, output):
    original=path.read_bytes();raw=bytearray(original)
    assert raw[:4]==b'RIFF' and raw[8:12]==b'AVI '
    discrepancy=len(raw)-(struct.unpack_from('<I',raw,4)[0]+8)
    # Observed Godot 4.7.2 writer bug: outer RIFF length is 70 bytes short;
    # all nested chunks and idx1 terminate exactly at EOF. Repair only that field.
    assert discrepancy in (0,70), 'Unknown RIFF size discrepancy'
    struct.pack_into('<I',raw,4,len(raw)-8)
    frames=[];header=None
    def walk(start,end):
        nonlocal header
        while start+8<=end:
            kind=raw[start:start+4];size=struct.unpack_from('<I',raw,start+4)[0]
            begin=start+8;stop=begin+size
            assert stop<=end
            if kind in [b'LIST',b'RIFF']:walk(begin+4,stop)
            elif kind==b'avih':header=struct.unpack_from('<14I',raw,begin)
            elif kind in [b'00dc',b'00db']:
                frame=raw[begin:stop]
                assert frame.startswith(b'\xff\xd8') and frame.endswith(b'\xff\xd9')
                frames.append(frame)
            start=stop+(size%2)
    walk(12,len(raw))
    assert header and len(frames)==header[4] and header[8:10]==(1366,768)
    normalized=path.parent/'validated';normalized.mkdir(exist_ok=True)
    (normalized/path.name).write_bytes(raw)
    output.mkdir(parents=True,exist_ok=True)
    selected=list(range(15,len(frames),30))
    for index in selected:(output/f'{path.stem}-{index:04d}.jpg').write_bytes(frames[index])
    return dict(file=path.name,sha256=hashlib.sha256(raw).hexdigest(),raw_sha256=hashlib.sha256(original).hexdigest(),riff_size_correction=discrepancy,bytes=len(raw),frames=len(frames),fps=1000000/header[0],duration_seconds=len(frames)*header[0]/1000000,resolution=list(header[8:10]),extracted_frames=selected,extraction='Original MJPEG bytes, no re-encoding; one frame per second for review',notes='MovieWriter uses project viewport 1366x768, while final PNG/report uses window 844x390; one initial engine frame precedes 900/360 scripted frames. Only outer RIFF length corrected, no frame/audio changes.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path)
    a=p.parse_args();results=[inspect(path,a.directory/'movie-frames') for path in sorted(a.directory.glob('*.avi'))]
    assert len(results)==2 and sorted(r['frames'] for r in results)==[361,901]
    (a.directory/'movie-validation.json').write_text(json.dumps(dict(status='pass',movies=results),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(results,indent=2))
