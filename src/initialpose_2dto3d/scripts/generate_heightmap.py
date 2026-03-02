#!/usr/bin/env python3
import argparse
import sys
import os

# Add parent directory to path to allow importing core module when run as a script
# This is for development/off-line use.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from initialpose_2dto3d.core.pcd_processor import heightmap_generation_workflow
except ImportError:
    # If installed as a package, it should be importable directly
    from core.pcd_processor import heightmap_generation_workflow

def main():
    parser = argparse.ArgumentParser(description='Generate heightmap.npy from PCD file.')
    parser.add_ignore = parser.add_argument('--pcd', type=str, required=True, help='Path to input PCD file')
    parser.add_argument('--yaml', type=str, required=True, help='Path to map.yaml to get origin and resolution')
    parser.add_argument('--out', type=str, default='heightmap.npy', help='Output .npy file path')
    
    # Optional overrides
    parser.add_argument('--res', type=float, help='Override resolution from YAML')
    parser.add_argument('--origin', type=float, nargs=3, help='Override origin [x, y, z] from YAML')
    parser.add_argument('--size', type=int, nargs=2, help='Grid size [width, height] (usually matches PGM image size)')

    args = parser.parse_args()

    success = heightmap_generation_workflow(
        pcd_path=args.pcd,
        map_yaml_path=args.yaml,
        output_npy_path=args.out,
        custom_res=args.res,
        custom_origin=args.origin,
        custom_size=args.size
    )

    if success:
        print("Done.")
    else:
        print("Failed.")
        sys.exit(1)

if __name__ == '__main__':
    main()
