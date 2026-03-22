import bpy
import bmesh
from mathutils import Matrix

def create_reachability_mesh(points, voxel_size=0.2):
    """
    Creates a real Blender object with meshes for each voxel.
    Optimized version using from_pydata for speed.
    """
    print(f"Generating Reachability Mesh for {len(points)} voxels...")
    
    # Check if object already exists and remove it to refresh
    if "Reachability_Map" in bpy.data.objects:
        old_obj = bpy.data.objects["Reachability_Map"]
        bpy.data.objects.remove(old_obj, do_unlink=True)

    mesh = bpy.data.meshes.new("ReachabilityMesh")
    obj = bpy.data.objects.new("Reachability_Map", mesh)
    bpy.context.collection.objects.link(obj)

    # Generate mesh data for all boxes at once
    # This is much faster than BMesh operators in a loop.
    verts, faces = [], []
    s = voxel_size * 0.45 # slight gap between voxels
    
    # Unit box vertices and faces
    box_v = [(-s, -s, -s), (s, -s, -s), (s, s, -s), (-s, s, -s),
             (-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s)]
    box_f = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 4, 7, 3), 
             (1, 5, 6, 2), (0, 1, 5, 4), (3, 2, 6, 7)]
    
    for i, p in enumerate(points):
        base = i * 8
        for v in box_v:
            verts.append((p[0] + v[0], p[1] + v[1], p[2] + v[2]))
        for f in box_f:
            faces.append((f[0] + base, f[1] + base, f[2] + base, f[3] + base))
            
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Create and assign a transparent blue material with emission
    mat_name = "ReachabilityMaterial"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.0, 0.5, 1.0, 1.0) # Neon Blue
            bsdf.inputs['Emission Color'].default_value = (0.0, 0.2, 1.0, 1.0)
            bsdf.inputs['Emission Strength'].default_value = 1.0
            bsdf.inputs["Alpha"].default_value = 0.5
        mat.blend_method = 'BLEND'
    
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    return obj
