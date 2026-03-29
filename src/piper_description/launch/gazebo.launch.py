from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_path = get_package_share_directory('piper_description')
    urdf_path = os.path.join(pkg_path, 'urdf', 'piper_description.urdf')

    with open(urdf_path, 'r') as f:
        robot_desc = f.read()

    return LaunchDescription([

        # ✅ Start Gazebo correctly
        ExecuteProcess(
            cmd=['gz', 'sim', '-r', 'empty.sdf'],
            output='screen'
        ),

        # Spawn robot
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-string', robot_desc, '-name', 'piper'],
            output='screen'
        )
    ])
