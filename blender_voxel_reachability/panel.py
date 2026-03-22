import bpy
from bpy.types import Panel, PropertyGroup

class ReachabilityProperties(PropertyGroup):
    voxel_size: bpy.props.FloatProperty(
        name="Voxel Size",
        description="Size of the voxels in meters (smaller is slower but more accurate)",
        default=0.2,
        min=0.05,
        max=2.0
    )
    
    viz_mode: bpy.props.EnumProperty(
        name="Visualization",
        description="Choose how to see the results",
        items=[
            ('mesh', "Mesh", "Create a permanent mesh object (Recommended)"),
            ('decor', "GPU Overlay", "Fast temporary overlay (Might show through walls)")
        ],
        default='mesh'
    )

class RECH_PT_panel(Panel):
    bl_label = "Reachability Analysis"
    bl_idname = "RECH_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Bonsai'  # This puts it in the same Sidebar tab as Bonsai

    def draw(self, context):
        layout = self.layout
        props = context.scene.reachability_props
        
        col = layout.column(align=True)
        col.prop(props, "voxel_size")
        col.prop(props, "viz_mode")
        
        layout.separator()
        
        # This button triggers the operator we wrote in operators.py
        layout.operator("reachability.run_analysis", icon='PLAY', text="Calculate Reachability")

classes = (
    ReachabilityProperties,
    RECH_PT_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.reachability_props = bpy.props.PointerProperty(type=ReachabilityProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.reachability_props
