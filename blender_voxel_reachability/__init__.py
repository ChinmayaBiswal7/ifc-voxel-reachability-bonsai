bl_info = {
    "name": "Voxel Reachability Analysis",
    "author": "GSoC Contributor",
    "version": (1, 0, 3),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Bonsai",
    "description": "Compute reachable space in IFC models using voxelization",
    "category": "Bonsai",
}

import bpy
import os
import sys

# Get the path to this addon
addon_dir = os.path.dirname(os.path.abspath(__file__))
voxec_dir = os.path.join(addon_dir, "voxec")

# Windows DLL loading help
if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
    try:
        os.add_dll_directory(voxec_dir)
        # Also add addon_dir just in case
        os.add_dll_directory(addon_dir)
    except:
        pass

from . import operators
from . import panel

def register():
    operators.register()
    panel.register()

def unregister():
    panel.unregister()
    operators.unregister()
