# initialpose_2dto3d

RViz2などの2Dナビゲーションツールから発行される2Dの初期位置（`geometry_msgs/PoseWithCovarianceStamped`）をSubscribeし、事前生成されたHeightMap（2.5D標高マップ）を参照してZ軸（高さ）を動的に補完した上で、3D LiDAR自己位置推定ノード向けの3D初期位置（`geometry_msgs/PoseStamped`）としてPublishするROS2パッケージです。

## 特徴
- **Z軸補完**: 事前にPCDから生成したHeightMap (.npy) を用いて、2D座標を3D座標に高精度に変換。
- **姿勢補正**: 受信した姿勢のYaw角を維持しつつ、Roll/Pitchを `0.0` にリセット。
- **オフラインツール同梱**: 3D点群 (PCD) から標高マップを生成するスクリプトを提供。
- **Docker対応**: ROS2 Humble環境が構築済みのDockerfileを提供。

## セットアップ

### 1. Docker環境の準備
ホストマシンにDockerおよびDocker Composeがインストールされている必要があります。

```bash
# プロジェクトルートに移動
cd initialpose_2dto3d

# コンテナのビルドと起動
docker compose up -d

# コンテナ内に入る
docker exec -it initialpose_2dto3d_container bash
```

### 2. ビルド (コンテナ内)
```bash
colcon build --symlink-install
source install/setup.bash
```

## 使用方法

### 1. HeightMapの生成 (オフライン)
お手持ちのPCDと `map.yaml` から標高マップデータを作成します。

```bash
ros2 run initialpose_2dto3d generate_heightmap --pcd map.pcd --yaml map.yaml --out map_height.npy
```

### 2. ノードの起動
Launchファイルを使用してノードを起動します。

```bash
ros2 launch initialpose_2dto3d initialpose_2dto3d.launch.py \
    map_yaml_path:=/path/to/map.yaml \
    heightmap_path:=/path/to/map_height.npy \
    default_z:=0.0
```

### パラメータ
- `input_topic`: Subscribeするトピック名 (デフォルト: `/initialpose_2d`)
- `output_topic`: Publishするトピック名 (デフォルト: `/initialpose`)
- `map_yaml_path`: `map.yaml` の絶対パス
- `heightmap_path`: 生成した `heightmap.npy` の絶対パス
- `default_z`: マップ外やデータ欠損時に使用するデフォルトの高さ

## システム構成
- **言語**: Python 3 (ROS2 Humble)
- **依存ライブラリ**: `numpy`, `pyyaml`, `scipy`, `open3d`
- **入力メッセージ**: `geometry_msgs/msg/PoseWithCovarianceStamped`
- **出力メッセージ**: `geometry_msgs/msg/PoseStamped`
