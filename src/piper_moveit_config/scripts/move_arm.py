#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    Constraints,
    JointConstraint,
    RobotState,
    PlanningScene,
)
from moveit_msgs.srv import ApplyPlanningScene
from sensor_msgs.msg import JointState

# BUG FIX #5: CollisionObject, SolidPrimitive, Pose were used in add_environment()
# but never imported at the top level — caused NameError crash at runtime.
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose


class MoveArm(Node):
    def __init__(self):
        super().__init__("move_arm")

        self.client = ActionClient(self, MoveGroup, "/move_action")

        self.get_logger().info("Waiting for move_group...")
        self.client.wait_for_server()
        self.get_logger().info("Connected!")

    def send_goal(self):
        goal_msg = MoveGroup.Goal()

        goal_msg.request.group_name = "arm"
        goal_msg.request.num_planning_attempts = 5
        goal_msg.request.allowed_planning_time = 5.0

        start = JointState()
        start.name = [
            "joint1", "joint2", "joint3",
            "joint4", "joint5", "joint6"
        ]
        start.position = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        robot_state = RobotState()
        robot_state.joint_state = start

        goal_msg.request.start_state = robot_state

        # ===== SIMPLE JOINT GOAL (SAFE) =====
        constraints = Constraints()
        target_positions = [0.0, -0.3, 0.3, 0.0, 0.3, 0.0]

        for i, joint_name in enumerate(start.name):
            jc = JointConstraint()
            jc.joint_name = joint_name
            jc.position = target_positions[i]
            jc.tolerance_above = 0.1
            jc.tolerance_below = 0.1
            jc.weight = 1.0
            constraints.joint_constraints.append(jc)

        goal_msg.request.goal_constraints.append(constraints)

        # BUG FIX #6: add_environment() was called before send_goal_async() but its
        # async service call was never spun/awaited — scene objects were often not applied
        # before MoveIt started planning. Now we apply the scene synchronously first.
        self.add_environment()

        # ===== SEND GOAL =====
        self.get_logger().info("Sending goal...")
        future = self.client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, future)

        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Goal rejected")
            return

        self.get_logger().info("Goal accepted, waiting for result...")
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result()
        self.get_logger().info(f"DONE — error code: {result.result.error_code.val}")

    def add_environment(self):
        self.scene_client = self.create_client(
            ApplyPlanningScene, "/apply_planning_scene"
        )

        while not self.scene_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for planning scene service...")

        scene = PlanningScene()
        scene.is_diff = True

        # ===== TABLE =====
        table = CollisionObject()
        table.id = "table"
        table.header.frame_id = "world"

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = [1.0, 1.0, 0.05]

        pose = Pose()
        pose.position.x = 0.5
        pose.position.y = 0.0
        pose.position.z = -0.025

        table.primitives.append(primitive)
        table.primitive_poses.append(pose)
        table.operation = CollisionObject.ADD

        # ===== CONTAINER =====
        container = CollisionObject()
        container.id = "container5"
        container.header.frame_id = "world"

        primitive2 = SolidPrimitive()
        primitive2.type = SolidPrimitive.BOX
        primitive2.dimensions = [0.1, 0.1, 0.15]

        pose2 = Pose()
        pose2.position.x = 0.6
        pose2.position.y = 0.3
        pose2.position.z = 0.075

        container.primitives.append(primitive2)
        container.primitive_poses.append(pose2)
        container.operation = CollisionObject.ADD

        # ===== PAN =====
        pan = CollisionObject()
        pan.id = "pan2"
        pan.header.frame_id = "world"

        primitive3 = SolidPrimitive()
        primitive3.type = SolidPrimitive.CYLINDER
        primitive3.dimensions = [0.1, 0.13]  # height, radius

        pose3 = Pose()
        pose3.position.x = 0.4
        pose3.position.y = -0.3
        pose3.position.z = 0.05

        pan.primitives.append(primitive3)
        pan.primitive_poses.append(pose3)
        pan.operation = CollisionObject.ADD

        scene.world.collision_objects = [table, container, pan]

        req = ApplyPlanningScene.Request()
        req.scene = scene

        # BUG FIX #6: Spin until the scene is actually applied before returning.
        # Previously this was fire-and-forget — planning could start before the
        # collision objects existed in the scene.
        future = self.scene_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        self.get_logger().info("Planning scene applied.")


def main():
    rclpy.init()
    node = MoveArm()
    node.send_goal()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
