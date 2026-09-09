"""Strict structural checks for the small, self-contained foundation GLB fixture."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import struct


def validate(path: Path) -> dict:
    raw = path.read_bytes()
    assert len(raw) < 100_000, "Unexpected sample growth"
    magic, version, length = struct.unpack_from("<4sII", raw)
    assert magic == b"glTF" and version == 2 and length == len(raw)
    chunks, offset = {}, 12
    while offset < length:
        size, kind = struct.unpack_from("<II", raw, offset)
        assert size % 4 == 0 and offset + 8 + size <= length
        assert kind not in chunks
        chunks[kind] = raw[offset + 8:offset + 8 + size]
        offset += 8 + size
    assert offset == length and set(chunks) == {0x4E4F534A, 0x004E4942}
    doc = json.loads(chunks[0x4E4F534A])
    binary = chunks[0x004E4942]
    assert doc["asset"]["version"] == "2.0"
    assert len(doc["buffers"]) == 1 and "uri" not in doc["buffers"][0]
    assert doc["buffers"][0]["byteLength"] <= len(binary)
    assert not doc.get("images") and not doc.get("textures"), "Sample must have no texture dependencies"
    assert len(doc["materials"]) == len(doc["meshes"]) == len(doc["skins"]) == 1
    assert doc["materials"][0].get("alphaMode", "OPAQUE") == "OPAQUE"
    assert len(doc["skins"][0]["joints"]) == 1
    for node in doc["nodes"]:
        assert re.fullmatch("[a-z][a-z0-9_]*", node["name"]), "Node naming"
        assert node.get("translation", [0,0,0]) == [0,0,0], "Floor origin / no offset"
        assert node.get("scale", [1,1,1]) == [1,1,1]
        assert "matrix" not in node
    views, accessors = doc["bufferViews"], doc["accessors"]
    for view in views:
        assert view.get("buffer", 0) == 0
        assert view.get("byteOffset", 0) + view["byteLength"] <= len(binary)
    formats = {5121:"B", 5123:"H", 5125:"I", 5126:"f"}
    sizes = {"SCALAR":1, "VEC2":2, "VEC3":3, "VEC4":4, "MAT4":16}
    def unpack(index: int) -> list[tuple]:
        a = accessors[index]
        view = views[a["bufferView"]]
        fmt = "<" + formats[a["componentType"]] * sizes[a["type"]]
        width = struct.calcsize(fmt)
        stride = view.get("byteStride", width)
        start = view.get("byteOffset", 0) + a.get("byteOffset", 0)
        assert a["count"] > 0 and a.get("byteOffset", 0) + (a["count"] - 1) * stride + width <= view["byteLength"]
        return [struct.unpack_from(fmt, binary, start + i * stride) for i in range(a["count"])]
    for index in range(len(accessors)):
        unpack(index)
    primitive = doc["meshes"][0]["primitives"][0]
    attrs = primitive["attributes"]
    assert {"POSITION","JOINTS_0","WEIGHTS_0"} <= attrs.keys()
    positions = unpack(attrs["POSITION"])
    bounds = [[min(p[i] for p in positions), max(p[i] for p in positions)] for i in range(3)]
    assert bounds == [[-0.5,0.5],[0.0,1.0],[-0.5,0.5]], f"One-meter Y-up floor origin: {bounds}"
    assert all(abs(sum(w)-1) < 1e-6 for w in unpack(attrs["WEIGHTS_0"]))
    assert all(all(j == 0 for j in joints) for joints in unpack(attrs["JOINTS_0"]))
    animations = doc["animations"]
    assert [a["name"] for a in animations] == ["idle"]
    rotation = next(c for c in animations[0]["channels"] if c["target"]["path"] == "rotation")
    sampler = animations[0]["samplers"][rotation["sampler"]]
    assert len(set(unpack(sampler["output"]))) > 1, "Animation must actually change pose"
    return dict(status="pass", sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
                gltf="2.0", meshes=1, skins=1, joints=1, materials=1, textures=0,
                animations=["idle"], bounds_meters=bounds, triangles=len(unpack(primitive["indices"])) // 3)


if __name__ == "__main__":
    import sys
    print(json.dumps(validate(Path(sys.argv[1])), indent=2))
