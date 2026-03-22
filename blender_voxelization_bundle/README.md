# blender_voxelization_bundle

A self-contained Blender addon that **bundles the `voxec` voxelization library**,
following the exact same pattern as `blender_voxel_reachability`.

---

## Folder structure

```
blender_voxelization_bundle/
├── __init__.py               ← Blender addon entry-point (path setup + register/unregister)
├── blender_manifest.toml     ← Blender 4.2+ extension manifest
├── README.md                 ← this file
└── voxec/                    ← bundled voxec package (mirrors blender_voxel_reachability/voxec/)
    ├── __init__.py           ← re-exports SWIG symbols + convenience run()
    ├── voxec.py              ← SWIG-generated Python wrapper (auto-generated, do not edit)
    └── _voxec.pyd            ← native extension – YOU MUST PLACE THIS FILE HERE
                                  Windows → _voxec.pyd  (cp311-win_amd64)
                                  Linux   → _voxec.so   (cp311-linux-x86_64)
```

---

## How to complete the bundle

The `voxec/` package needs the pre-compiled native extension `_voxec.pyd` (Windows)
or `_voxec.so` (Linux) to work.  Copy it from your platform-specific build:

### Windows (already done in `blender_voxel_reachability`)
```powershell
Copy-Item "blender_voxel_reachability\voxec\_voxec.pyd" `
          "blender_voxelization_bundle\voxec\_voxec.pyd"
```

### Linux
```bash
cp voxec-52c54ed-linux64-py311/voxec/_voxec.so \
   blender_voxelization_bundle/voxec/_voxec.so
```

---

## How voxec is bundled (same as `blender_voxel_reachability`)

1. **`__init__.py` (addon root)** adds the addon directory to `sys.path` and
   calls `os.add_dll_directory()` on Windows so the native `.pyd` is found.
2. **`voxec/__init__.py`** does `from .voxec import *` (identical to the Linux
   bundle's `__init__.py`) and defines the same `run()` convenience wrapper.
3. **`voxec/voxec.py`** is the SWIG-auto-generated wrapper – **do not modify**.
4. **`voxec/_voxec.pyd`** is the compiled C++ extension – platform-specific binary.

---

## Using this bundle from another addon

```python
import sys, os

# Point to this bundle's directory so `import voxec` resolves here
bundle_dir = r"C:\path\to\blender_voxelization_bundle"
if bundle_dir not in sys.path:
    sys.path.insert(0, bundle_dir)

import voxec

result = voxec.run("voxelize", input="MyModel.ifc")
```
