# 🚀 Reachability Analysis for IFC (Bonsai Integration)

This project provides a native Blender Addon and Extension for high-performance reachability analysis within building IFC models. It integrates directly with the **Bonsai (BlenderBIM)** ecosystem.

## 🌟 GSoC 2024 Proof of Concept
This repository demonstrates a production-ready approach for spatial analysis in BIM workflows:
- **Native Library Bundling**: The `voxec` C++ binary is fully bundled inside a Blender Extension, making it a zero-installation, self-contained tool.
- **Bonsai UI Integration**: A custom UI panel is integrated directly into the Bonsai sidebar.
- **Automated Pathfinding**: High-speed voxelization and reachability traversal (seed/region analysis) of complex IFC geometry.

## 📁 Key Components
- **`blender_voxel_reachability`**: The main Blender Addon and Bonsai UI integration.
- **`blender_voxelization_bundle`**: The self-contained extension containing pre-compiled `voxec` binaries for Windows and Linux.
- **`reachability.py`**: The core Python math logic and algorithm implementation for voxel processing.
- **`view_mesh.py`**: High-performance mesh generation for visualizing 3D reachable volumes directly in the Blender viewport.

## 🛠 Installation (Blender 4.2+)
1. Download the `blender_voxelization_bundle.zip` and `blender_voxel_reachability.zip`.
2. In Blender, go to **Edit > Preferences > Add-ons**.
3. Click **Install...** and select `blender_voxelization_bundle.zip` first, then `blender_voxel_reachability.zip`.
4. Ensure **Bonsai** is installed and an IFC model is loaded.

## 🖥 Usage
1. Open an IFC model using the Bonsai importer.
2. Navigate to the **Bonsai Tool Sidebar** in the 3D View.
3. Locate the **Reachability Analysis** tab.
4. Set your desired **Voxel Size** (0.4m recommended for stability) and click **Calculate Reachability**.
5. The result will be generated as a mesh object in your scene.

## ⚙️ Technical Highlights
- **Grid Alignment Fix**: Solved complex floating-point precision errors from Blender's UI to ensure perfectly aligned voxel grids for boolean operations.
- **Threading Stability**: Optimized for Blender's single-threaded Python environment to prevent memory crashes during heavy voxelization loops.
- **Automated Geometry Extraction**: Intelligently extracts Floors (Slabs), Walkable Surfaces, and Entry Points (Doors) directly from IFC classes using `ifcopenshell`.

## 📜 Requirements
- **Blender 4.2+**
- **Bonsai (formerly BlenderBIM)**
- `ifcopenshell` (included with Bonsai)
- `numpy` (included with Blender)

---
*Developed as part of the GSoC 2024 proposal for OSArch / Bonsai.*
