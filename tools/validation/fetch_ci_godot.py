"""CI-only official pinned engine download, never a local/global auto-install."""
import hashlib
import io
import json
import os
from pathlib import Path
import urllib.request
import zipfile

if os.environ.get("GITHUB_ACTIONS") != "true":
    raise SystemExit("CI-only helper. Locally detect/report tools first; provide an existing Godot path.")
root = Path(__file__).resolve().parents[2] / ".work/tools"
root.mkdir(parents=True, exist_ok=True)
name = "Godot_v4.7.2-stable_linux.x86_64.zip"
request = urllib.request.Request("https://api.github.com/repos/godotengine/godot-builds/releases/tags/4.7.2-stable", headers={"User-Agent":"HeroSmash-foundation-ci"})
with urllib.request.urlopen(request, timeout=30) as response:
    release = json.load(response)
asset = next(a for a in release["assets"] if a["name"] == name)
url = "https://github.com/godotengine/godot-builds/releases/download/4.7.2-stable/" + name
assert asset["browser_download_url"] == url
with urllib.request.urlopen(url, timeout=60) as response:
    payload = response.read()
actual = "sha256:" + hashlib.sha256(payload).hexdigest()
assert asset.get("digest") == actual, "Official release digest missing/mismatched"
with zipfile.ZipFile(io.BytesIO(payload)) as archive:
    for info in archive.infolist():
        assert (root / info.filename).resolve().is_relative_to(root.resolve())
    archive.extractall(root)
engine = root / name.removesuffix(".zip")
engine.chmod(0o755)
print(f"Verified official Godot 4.7.2 portable runner tool: {actual}")
