bl_info = {
    "name": "Voxelization Bundle",
    "author": "GSoC Contributor",
    "version": (1, 0, 1),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Bonsai",
    "description": "Bundles the voxec voxelization library for use inside Blender",
    "category": "Bonsai",
}

import bpy
import os
import sys
import traceback

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
addon_dir = os.path.dirname(os.path.abspath(__file__))
voxec_dir = os.path.join(addon_dir, "voxec")

# Store the error message to show in the UI
last_error = ""

# Windows DLL loading help
if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
    for _d in (voxec_dir, addon_dir):
        try:
            if os.path.exists(_d):
                os.add_dll_directory(_d)
        except Exception as e:
            last_error = f"DLL path error: {str(e)}"

# Put the addon directory on sys.path
if addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)

# ---------------------------------------------------------------------------
# Import Check
# ---------------------------------------------------------------------------
try:
    import voxec
    print(f"[blender_voxelization_bundle] voxec loaded from: {voxec.__file__}")
except Exception:
    last_error = traceback.format_exc()
    print(f"[blender_voxelization_bundle] ERROR loading voxec:\n{last_error}")

# ---------------------------------------------------------------------------
# Status Panel
# ---------------------------------------------------------------------------
class VOX_PT_bundle_status(bpy.types.Panel):
    bl_label = "Voxelization Bundle"
    bl_idname = "VOX_PT_bundle_status"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bonsai'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        if not last_error:
            try:
                import voxec
                layout.label(text="Voxec Library Ready", icon='CHECKMARK')
                layout.label(text=f"File: {os.path.basename(voxec.__file__)}")
            except Exception as e:
                layout.label(text="Import failed after init", icon='ERROR')
                layout.label(text=str(e))
        else:
            layout.label(text="Bundle Error", icon='ERROR')
            # Split error message into multiple labels if too long
            for line in last_error.split('\n')[-3:]: # Show last 3 lines of traceback
                if line.strip():
                    layout.label(text=line)

# ---------------------------------------------------------------------------
# Blender register / unregister
# ---------------------------------------------------------------------------
classes = (
    VOX_PT_bundle_status,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    print("[blender_voxelization_bundle] registered.")

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("[blender_voxelization_bundle] unregistered.")
