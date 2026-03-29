from launch import LaunchDescription
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_demo_launch


def generate_launch_description():
    moveit_config = (
        MoveItConfigsBuilder("piper", package_name="piper_moveit_config")
        .to_moveit_configs()
    )
    # generate_demo_launch handles everything:
    # robot_state_publisher, move_group, RViz, ros2_control_node, spawn_controllers
    # It reads ros2_controllers.yaml (plural) from config/ automatically.
    # Make sure your file is named ros2_controllers.yaml (not ros2_controller.yaml).
    return LaunchDescription([
        generate_demo_launch(moveit_config),
    ])
