import bpy
import os
import sys

# Add current directory to path so we can import our modules
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import reachability

class ReachabilityProperties(bpy.types.PropertyGroup):
    voxel_size: bpy.props.FloatProperty(
        name="Voxel Size",
        description="Size of the voxels in meters",
        default=0.2,
        min=0.01,
        max=2.0
    )
    
    viz_mode: bpy.props.EnumProperty(
        name="Visualization",
        description="How to display the results",
        items=[
            ('mesh', "Mesh", "Create a physical mesh object (Recommended)"),
            ('decor', "GPU Overlay", "Fast temporary GPU overlay (Shows through walls)")
        ],
        default='mesh'
    )

class REACHABILITY_OT_run(bpy.types.Operator):
    bl_idname = "reachability.run"
    bl_label = "Calculate Reachability"
    bl_description = "Run reachability analysis on the current IFC project"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.reachability_props
        
        # Try to get the IFC file from Bonsai (BlenderBIM)
        ifc_file = None
        try:
            import blenderbim.tool as tool
            ifc_file = tool.Ifc.get()
            print("Successfully retrieved IFC model from Bonsai.")
        except ImportError:
            self.report({'WARNING'}, "Bonsai (BlenderBIM) not found. This tool works best with Bonsai installed.")
            # Fallback: check if there are any IFC files in the current folder or explicitly opened
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to get IFC file: {e}")
            return {'CANCELLED'}

        if not ifc_file:
            self.report({'ERROR'}, "No active IFC project found in Bonsai. Please load a project first.")
            return {'CANCELLED'}

        # Run the heavy computation
        try:
            # Note: run_analysis takes a list of files
            reachability.run_analysis(
                [ifc_file], 
                mode=props.viz_mode, 
                voxel_size=props.voxel_size
            )
            self.report({'INFO'}, "Reachability analysis complete.")
        except Exception as e:
            self.report({'ERROR'}, f"Analysis failed: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

class REACHABILITY_PT_panel(bpy.types.Panel):
    bl_label = "Reachability Analysis"
    bl_idname = "REACHABILITY_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BIM'  # Puts it in the "BIM" sidebar tab next to Bonsai

    def draw(self, context):
        layout = self.layout
        props = context.scene.reachability_props
        
        col = layout.column(align=True)
        col.prop(props, "voxel_size")
        col.prop(props, "viz_mode")
        
        layout.separator()
        
        layout.operator("reachability.run", icon='PLAY')

classes = (
    ReachabilityProperties,
    REACHABILITY_OT_run,
    REACHABILITY_PT_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.reachability_props = bpy.props.PointerProperty(type=ReachabilityProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.reachability_props

if __name__ == "__main__":
    register()
