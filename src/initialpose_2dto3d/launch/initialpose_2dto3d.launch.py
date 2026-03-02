import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Declare arguments
    input_topic_arg = DeclareLaunchArgument(
        'input_topic', default_value='/initialpose_2d',
        description='Topic name for input 2D pose'
    )
    output_topic_arg = DeclareLaunchArgument(
        'output_topic', default_value='/initialpose',
        description='Topic name for output 3D pose'
    )
    map_yaml_path_arg = DeclareLaunchArgument(
        'map_yaml_path', default_value='',
        description='Absolute path to map.yaml'
    )
    heightmap_path_arg = DeclareLaunchArgument(
        'heightmap_path', default_value='',
        description='Absolute path to heightmap.npy'
    )
    default_z_arg = DeclareLaunchArgument(
        'default_z', default_value='0.0',
        description='Default Z value when heightmap is not available'
    )

    # Node configuration
    node = Node(
        package='initialpose_2dto3d',
        executable='initialpose_2dto3d_node',
        name='initialpose_2dto3d_node',
        output='screen',
        parameters=[{
            'input_topic': LaunchConfiguration('input_topic'),
            'output_topic': LaunchConfiguration('output_topic'),
            'map_yaml_path': LaunchConfiguration('map_yaml_path'),
            'heightmap_path': LaunchConfiguration('heightmap_path'),
            'default_z': LaunchConfiguration('default_z'),
        }]
    )

    return LaunchDescription([
        input_topic_arg,
        output_topic_arg,
        map_yaml_path_arg,
        heightmap_path_arg,
        default_z_arg,
        node
    ])
