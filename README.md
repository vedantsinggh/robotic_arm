# Robotic Manipulation using MoveIt (ROS 2)

## Overview

This project implements a robotic manipulation pipeline using ROS 2 and MoveIt. The system enables a 6-DOF robotic arm to perform structured motion planning tasks in a predefined workspace consisting of containers and pans.

The current implementation focuses on reliable motion planning, collision avoidance, and deterministic execution using RViz.

## Features

- Motion planning using MoveIt (OMPL - RRTConnect)
- Collision-aware environment using planning scene
- Predefined target-based navigation
- Menu-driven execution
- Deterministic and repeatable task execution

## System Architecture

- ROS 2 for communication and system integration
- MoveIt for motion planning and execution
- URDF-based robot model
- Planning Scene for environment representation

## Workspace Description

The workspace is modeled using primitive geometries:

- Table: Box
- Containers: Grid of small boxes
- Pan: Box

All objects are defined in the `base_link` frame.

## Task Description

The system performs a simple structured task:

1. Move to container location
2. Move to pan location
3. Return to home position

## Current Status

- Task 1 successfully implemented
- System operates in RViz
- Demonstration video provided separately

## Installation

```bash
git clone https://github.com/vedantsinggh/robotic_arm.git
cd robotic_arm
colcon build
source ./install/setup.bash
```

## Usage

Start MoveIt:

```bash
ros2 launch piper_moveit_config demo.launch.py
```

Run the task node:

```bash
ros2 run piper_task move_arm
```

Follow the menu in the terminal to execute tasks.

## Design Decisions

- Primitive shapes used instead of STL meshes for performance
- Joint-space planning used for stability
- Predefined targets used instead of perception

## Limitations

- No gripper or grasp execution
- No perception system
- No physics simulation
- Static target definitions

## Future Work

- Integration with Gazebo
- Gripper and grasp planning
- Vision-based object detection
- Dynamic task planning

## Repository

https://github.com/vedantsinggh/robotic_arm

## License

This project is licensed under the Apache 2.0 License.
