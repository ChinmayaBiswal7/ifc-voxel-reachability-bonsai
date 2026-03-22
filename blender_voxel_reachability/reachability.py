import functools
import sys
import ifcopenshell
import ifcopenshell.geom
import concurrent.futures
import os
import numpy as np

# Try to import voxec from the bundle first, then local
try:
    import voxec
except ImportError:
    from . import voxec 

# Ensure helper modules can be found
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# GLOBAL VOXEC CONTEXT (FOR ALIGNMENT)
_ctx = voxec.context()

def run_vox(op, *args, **kwargs):
    # ONE shared context = all grids aligned (fixes "unaligned voxel grids" error).
    # THREADS=1 = no multi-thread crash inside Blender.
    # All 3 variables MUST be set every time.
    _ctx.set('VOXELSIZE', voxec.default_VOXELSIZE)
    _ctx.set('CHUNKSIZE', voxec.default_CHUNKSIZE)
    _ctx.set('THREADS', 1)
    return voxec.run_(op, args, kwargs, _ctx, True)  # True = silent



# create_geometry takes a LIST of ifcopenshell.file objects (original design)
def create_geometry(files, **kwargs):
    s = ifcopenshell.geom.settings(
        USE_WORLD_COORDS=True,
        DISABLE_OPENING_SUBTRACTIONS=False,
        ITERATOR_OUTPUT=ifcopenshell.ifcopenshell_wrapper.SERIALIZED,
    )

    def inner():
        for f in files:
            print(f"DEBUG: Iterating file type={type(f)}")
            it = ifcopenshell.geom.iterator(s, f, **kwargs, num_threads=2)
            if not it.initialize(): 
                print(f"DEBUG: Iterator failed to initialize for {type(f)}")
                return
            while True:
                elem = it.get()
                inst = f[elem.id]
                yield inst, elem.geometry.brep_data
                if not it.next(): break
    
    return list(inner())

def voxelize(geoms, label="Elements"):
    if not geoms: 
        print(f"No {label} found to voxelize.")
        return None
    
    combined_voxels = None
    total = len(geoms)
    print(f"Voxelizing {total} {label}...")
    
    for i, inst_geom in enumerate(geoms):
        if i > 300: # Safety limit - prevents out-of-memory crash in Blender
            print(f"Reached safety limit of 300 elements.")
            break
        try:
            new_vox = run_vox("voxelize", inst_geom[1], method="volume")
            if combined_voxels is None: combined_voxels = new_vox
            else: combined_voxels = combined_voxels.boolean_union(new_vox)
            if i % 200 == 0: print(f"Progress: {i}/{total} {label} done...")
        except Exception as e:
            print(f"Voxelize error on element {i}: {e}")
            continue
    return combined_voxels

def get_reachability(files, surface_voxels):
    print("\n--- TRAVERSAL ANALYSIS ---")
    slabs = create_geometry(files, include=["IfcSlab"])
    slab_voxels = voxelize(slabs, "Floors")
    doors = create_geometry(files, include=["IfcDoor"])
    door_voxels = voxelize(doors, "Openings")

    if not slab_voxels: 
        print("Fallback to shell")
        slab_voxels = surface_voxels
    if not door_voxels:
        door_voxels = slab_voxels

    # Restore exactly the original pathfinding logic sequence
    walkable = run_vox('shift', slab_voxels, dx=0, dy=0, dz=1)
    walkable_minus = run_vox('subtract', walkable, slab_voxels)
    walkable_seed = run_vox('intersect', door_voxels, walkable_minus)
    surfaces_sweep = run_vox('sweep', surface_voxels, dx=0, dy=0, dz=0.5)
    surfaces_padded = run_vox('offset_xy', surface_voxels, 0.1)
    surfaces_obstacle = run_vox('sweep', surfaces_padded, dx=0, dy=0, dz=-0.5)
    walkable_region = run_vox('subtract', surfaces_sweep, surfaces_obstacle)
    walkable_seed_real = run_vox('subtract', walkable_seed, surfaces_padded)
    
    print(f"Surface: {surface_voxels.count() if surface_voxels else 0}")
    print(f"Slabs: {slab_voxels.count() if slab_voxels else 0}")
    print(f"Doors: {door_voxels.count() if door_voxels else 0}")
    print(f"Seed: {walkable_seed_real.count() if walkable_seed_real else 0}")
    print(f"Region: {walkable_region.count() if walkable_region else 0}")

    if not walkable_region or not walkable_seed_real or walkable_seed_real.count() == 0:
        print("Warning: Traversal impossible.")
        return surface_voxels

    return run_vox('traverse', walkable_region, walkable_seed_real)

# Takes a LIST of ifcopenshell.file objects 
def run_analysis(ifc_files, mode="mesh", voxel_size=0.2):
    # CRITICAL: Clean up float precision errors coming from Blender UI (0.2000000298 => 0.2)
    clean_vsize = round(float(voxel_size), 3)
    safe_vsize = max(0.4, clean_vsize)
    voxec.default_VOXELSIZE = safe_vsize
    voxec.default_THREADS = 1  # Single-thread to avoid Blender Python crash

    
    print(f"\n--- REACHABILITY (Voxel: {safe_vsize}) ---")
    print(f"Files: {len(ifc_files)} | Types: {[type(f) for f in ifc_files]}")
    
    sh_classes = [
        "IfcWall", "IfcSlab", "IfcStair", "IfcStairFlight", 
        "IfcRamp", "IfcRampFlight"
    ]
    all_surfaces = create_geometry(ifc_files, include=sh_classes)
    
    surface_voxels = voxelize(all_surfaces, "Building Shell")
    if surface_voxels is None: 
        print("Error: No building elements found.")
        return 0

    reachable = get_reachability(ifc_files, surface_voxels)
    
    count = reachable.count() if reachable else 0
    print(f"TOTAL REACHABLE VOXELS: {count}")
    
    plot(reachable if count > 0 else surface_voxels, mode=mode, voxel_size=safe_vsize)
    return count

def plot(vx, mode="mesh", voxel_size=0.2):
    arr = np.array(vx.get_domain())
    if arr.sum() == 0: return
    voxels_set = np.array(np.where(arr)).T
    try:
        import bpy
        from . import view_mesh
        view_mesh.create_reachability_mesh(voxels_set, voxel_size=voxel_size)
    except Exception as e:
        print(f"Plot error: {e}")
