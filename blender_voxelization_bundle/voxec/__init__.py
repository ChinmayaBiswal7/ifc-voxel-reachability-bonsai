"""
blender_voxelization_bundle/voxec/__init__.py
---------------------------------------------
Package init for the bundled copy of voxec.

This file mirrors the structure used in blender_voxel_reachability/voxec/__init__.py.
It re-exports everything from voxec.py (the SWIG-generated wrapper) and
exposes the same default constants + convenience run() function.
"""

from .voxec import *  # re-export all SWIG-generated symbols

import multiprocessing

# ---------------------------------------------------------------------------
# Default context values — keep in sync with blender_voxel_reachability
# ---------------------------------------------------------------------------
default_VOXELSIZE = 0.2          # metres; same default as the Blender UI slider
default_CHUNKSIZE = 16           # voxel chunks
default_THREADS   = multiprocessing.cpu_count()
SILENT            = False        # set True to suppress voxec progress output

# ---------------------------------------------------------------------------
# Convenience wrapper — same signature as the blender_voxel_reachability build
# ---------------------------------------------------------------------------
def run(name, *args, **kwargs):
    """
    Execute a named voxec operation with a pre-configured context.

    Mirrors blender_voxel_reachability/voxec/__init__.py::run() exactly so
    any code that worked against the existing bundle also works here.

    Parameters
    ----------
    name : str
        The voxec operation name (e.g. 'voxelize', 'traverse', …).
    *args, **kwargs
        Positional / keyword arguments forwarded to the native run_() call.

    Returns
    -------
    result of voxec.run_()
    """
    ctx = context()
    ctx.set('VOXELSIZE', default_VOXELSIZE)
    ctx.set('CHUNKSIZE', default_CHUNKSIZE)
    ctx.set('THREADS',   default_THREADS)
    return run_(name, args, kwargs, ctx, SILENT)
