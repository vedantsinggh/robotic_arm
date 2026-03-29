from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_path = get_package_share_directory('piper_description')
    urdf_path = os.path.join(pkg_path, 'urdf', 'piper_description.urdf')

    # 👉 path to your SDF files (you create these)
    task_pkg = get_package_share_directory('piper_task')
    container_sdf = os.path.join(task_pkg, 'models', 'container.sdf')
    pan_sdf = os.path.join(task_pkg, 'models', 'pan.sdf')

    with open(urdf_path, 'r') as f:
        robot_desc = f.read()

    return LaunchDescription([

        # 🔹 Start Gazebo
        ExecuteProcess(
            cmd=['gz', 'sim', '-r', 'empty.sdf'],
            output='screen'
        ),

        # 🔹 Spawn robot
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-string', robot_desc, '-name', 'piper'],
            output='screen'
        ),

        # 🔴 Spawn container_5
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-file', container_sdf,
                '-name', 'container_5',
                '-x', '0.2',
                '-y', '0.0',
                '-z', '0.0'
            ],
            output='screen'
        ),

        # 🔵 Spawn pan_2
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-file', pan_sdf,
                '-name', 'pan_2',
                '-x', '0.4',
                '-y', '-0.2',
                '-z', '0.0'
            ],
            output='screen'
        ),
    ])
