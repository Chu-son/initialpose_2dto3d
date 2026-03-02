import numpy as np
import open3d as o3d
import yaml
import os
from scipy.interpolate import NearestNDInterpolator

def load_pcd(pcd_path):
    """Loads PCD file using Open3D."""
    if not os.path.exists(pcd_path):
        raise FileNotFoundError(f"PCD file not found: {pcd_path}")
    pcd = o3d.io.read_point_cloud(pcd_path)
    return pcd

def filter_points(pcd, voxel_size=0.1):
    """Downsamples point cloud and removes outliers."""
    pcd = pcd.voxel_down_sample(voxel_size=voxel_size)
    # Statistical outlier removal
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
    return pcd

def project_to_grid(pcd, origin, resolution, width, height, percentile=5):
    """
    Projects 3D points to 2D grid and calculates Z based on percentile.
    percentile=5 means we take the lower 5% to find the ground level robustly.
    """
    points = np.asarray(pcd.points)
    
    # Calculate grid indices
    u = ((points[:, 0] - origin[0]) / resolution).astype(int)
    v = ((points[:, 1] - origin[1]) / resolution).astype(int)

    # Filter points within bounds
    mask = (u >= 0) & (u < width) & (v >= 0) & (v < height)
    u_valid = u[mask]
    v_valid = v[mask]
    z_valid = points[mask, 2]

    # Initialize grid with NaN
    grid = np.full((height, width), np.nan)
    
    # Store Z values in a dictionary of lists for each grid cell
    # Note: For large clouds, this might be slow. Optimization could be needed.
    # However, this script is offline.
    cells = {}
    for idx in range(len(u_valid)):
        key = (v_valid[idx], u_valid[idx])
        if key not in cells:
            cells[key] = []
        cells[key].append(z_valid[idx])

    # Calculate percentile for each cell
    for (v_idx, u_idx), values in cells.items():
        grid[v_idx, u_idx] = np.percentile(values, percentile)

    return grid

def fill_holes(grid):
    """Fills NaN holes in the grid using Nearest Neighbor interpolation."""
    h, w = grid.shape
    v, u = np.indices(grid.shape)
    
    # Prepare points with known values
    mask_known = ~np.isnan(grid)
    if not np.any(mask_known):
        return grid # Nothing to interpolate

    coords_known = np.column_stack((v[mask_known], u[mask_known]))
    values_known = grid[mask_known]
    
    # Create interpolator
    interp = NearestNDInterpolator(coords_known, values_known)
    
    # Interpolate for NaN values
    mask_nan = np.isnan(grid)
    coords_nan = np.column_stack((v[mask_nan], u[mask_nan]))
    grid[mask_nan] = interp(coords_nan)
    
    return grid

def heightmap_generation_workflow(pcd_path, map_yaml_path, output_npy_path, 
                                  custom_res=None, custom_origin=None, custom_size=None):
    """Sequential workflow for generating heightmap."""
    print(f"Starting heightmap generation from {pcd_path}...")
    
    # 1. Load Map Config
    res = 0.05
    origin = [0.0, 0.0, 0.0]
    width = 0
    height = 0
    
    if map_yaml_path and os.path.exists(map_yaml_path):
        with open(map_yaml_path, 'r') as f:
            data = yaml.safe_load(f)
            res = data.get('resolution', res)
            origin = data.get('origin', origin)
            # Size usually comes from the image file associated with yaml
            # but we might need it as a parameter or calculate from image dimension.
            # For simplicity, we assume custom_size if not specified.
    
    if custom_res: res = custom_res
    if custom_origin: origin = custom_origin
    if custom_size:
        width, height = custom_size
    else:
        # If size not provided, we need to find it from PCD or YAML
        # This is a bit tricky without the .pgm file.
        # Let's assume the user provides it or we derive from PCD bounding box.
        pass

    # 2. Load and filter PCD
    pcd = load_pcd(pcd_path)
    pcd = filter_points(pcd)
    
    # Determine grid size if not provided
    if width == 0 or height == 0:
        bbox = pcd.get_axis_aligned_bounding_box()
        max_bound = bbox.get_max_bound()
        width = int((max_bound[0] - origin[0]) / res) + 1
        height = int((max_bound[1] - origin[1]) / res) + 1
        print(f"Auto-calculated grid size: {width}x{height}")

    # 3. Project to grid
    print(f"Projecting points to {width}x{height} grid...")
    grid = project_to_grid(pcd, origin, res, width, height)
    
    # 4. Fill holes
    print("Filling holes...")
    grid = fill_holes(grid)
    
    # 5. Save
    np.save(output_npy_path, grid)
    print(f"Success! Heightmap saved to {output_npy_path}")
    return True
