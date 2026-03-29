from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_path = get_package_share_directory('piper_description')
    urdf_path = os.path.join(pkg_path, 'urdf', 'piper_description.urdf')

    # ✅ define robot_desc properly
    with open(urdf_path, 'r') as f:
        robot_desc = f.read()

    return LaunchDescription([

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc}]
        ),

        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui'
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', os.path.expanduser('~/.piper.rviz')],
            parameters=[{'robot_description': robot_desc}]
        )
    ])
