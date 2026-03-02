import os
import yaml
import numpy as np

class HeightMapHandler:
    def __init__(self, map_yaml_path='', heightmap_path='', default_z=0.0, logger=None):
        self.logger = logger
        self.resolution = 0.05  # Default
        self.origin_x = 0.0
        self.origin_y = 0.0
        self.heightmap = None
        self.default_z = default_z
        self.is_heightmap_enabled = False

        if map_yaml_path:
            self._load_map_yaml(map_yaml_path)
        
        if heightmap_path:
            self._load_heightmap(heightmap_path)

    def _log_warn(self, msg):
        if self.logger:
            self.logger.warning(msg)
        else:
            print(f"[WARN] {msg}")

    def _log_info(self, msg):
        if self.logger:
            self.logger.info(msg)
        else:
            print(f"[INFO] {msg}")

    def _load_map_yaml(self, path):
        if not os.path.exists(path):
            self._log_warn(f"Map YAML file not found: {path}")
            return
        
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                self.resolution = data.get('resolution', 0.05)
                origin = data.get('origin', [0.0, 0.0, 0.0])
                self.origin_x = origin[0]
                self.origin_y = origin[1]
                self._log_info(f"Loaded map config: res={self.resolution}, origin=[{self.origin_x}, {self.origin_y}]")
        except Exception as e:
            self._log_warn(f"Failed to parse map YAML: {e}")

    def _load_heightmap(self, path):
        if not path or not os.path.exists(path):
            self._log_warn("Heightmap path is empty or file not found. Falling back to default_z mode.")
            return

        try:
            self.heightmap = np.load(path)
            self.is_heightmap_enabled = True
            self._log_info(f"Loaded heightmap from {path}. Shape: {self.heightmap.shape}")
        except Exception as e:
            self._log_warn(f"Failed to load heightmap .npy: {e}")

    def get_z_at(self, x, y):
        if not self.is_heightmap_enabled or self.heightmap is None:
            return self.default_z

        # Calculate indices
        u = int((x - self.origin_x) / self.resolution)
        v = int((y - self.origin_y) / self.resolution)

        # Check bounds (heightmap is expected to be [height, width] corresponding to [v, u])
        h, w = self.heightmap.shape
        if 0 <= u < w and 0 <= v < h:
            z = self.heightmap[v, u]
            if np.isnan(z) or np.isinf(z):
                self._log_warn(f"Value at ({x}, {y}) -> ({u}, {v}) is NaN/Inf. Using default_z.")
                return self.default_z
            return float(z)
        else:
            self._log_warn(f"Position ({x}, {y}) is out of heightmap bounds (index: {u}, {v}). Using default_z.")
            return self.default_z
