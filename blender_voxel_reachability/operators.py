import bpy
from . import reachability

class RECH_OT_run_analysis(bpy.types.Operator):
    bl_idname = "reachability.run_analysis"
    bl_label = "Run Reachability Analysis"
    bl_description = "Calculates reachable space based on the active IFC model in Bonsai"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.reachability_props
        
        # 1. Get IFC file from Bonsai
        raw_ifc = None
        try:
            import bonsai.tool as tool
            raw_ifc = tool.Ifc.get()
        except ImportError:
            try:
                import blenderbim.tool as tool
                raw_ifc = tool.Ifc.get()
            except ImportError:
                self.report({'ERROR'}, "Bonsai not found.")
                return {'CANCELLED'}

        if not raw_ifc:
            self.report({'ERROR'}, "No active IFC project found. Open an IFC file in Bonsai first.")
            return {'CANCELLED'}

        print(f"DEBUG IFC type: {type(raw_ifc)}")
        
        # THE KEY FIX:
        # tool.Ifc.get() returns an ifcopenshell.file object directly.
        # create_geometry() expects a LIST of file objects.
        # So we wrap it: [raw_ifc]
        ifc_files = [raw_ifc]
        
        self.report({'INFO'}, f"Starting Pathfinding Analysis (Voxel Size: {props.voxel_size})...")
        
        try:
            voxel_count = reachability.run_analysis(
                ifc_files,        # Pass as a list — this is how create_geometry expects it
                mode=props.viz_mode, 
                voxel_size=props.voxel_size
            )
            
            if voxel_count and voxel_count > 0:
                self.report({'INFO'}, f"Analysis Succeeded: {voxel_count} voxels found!")
            else:
                self.report({'WARNING'}, "No reachable paths found. Check the console for details.")
                
        except Exception as e:
            self.report({'ERROR'}, f"Analysis crashed: {str(e)}")
            import traceback
            traceback.print_exc()

        return {'FINISHED'}

def register():
    bpy.utils.register_class(RECH_OT_run_analysis)

def unregister():
    bpy.utils.unregister_class(RECH_OT_run_analysis)
