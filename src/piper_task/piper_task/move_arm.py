import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, PositionConstraint
from geometry_msgs.msg import PoseStamped
from shape_msgs.msg import SolidPrimitive
from moveit_msgs.msg import CollisionObject, PlanningScene
from moveit_msgs.srv import ApplyPlanningScene
import time


class MoveArm(Node):
    def __init__(self):
        super().__init__('move_arm')

        self.client = ActionClient(self, MoveGroup, '/move_action')
        self.add_environment()   # ✅ ADD THIS

    def move_to_pose(self, x, y, z):
        self.client.wait_for_server()

        goal = MoveGroup.Goal()

        goal.request.group_name = "arm"
        goal.request.num_planning_attempts = 5
        goal.request.allowed_planning_time = 5.0

        pose = PoseStamped()
        pose.header.frame_id = "base_link"
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z
        pose.pose.orientation.w = 1.0

        # --- Constraint ---
        constraint = Constraints()

        pos_constraint = PositionConstraint()
        pos_constraint.header.frame_id = "base_link"
        pos_constraint.link_name = "link6"   # ⚠️ change if needed

        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = [0.02, 0.02, 0.02]

        pos_constraint.constraint_region.primitives.append(box)
        pos_constraint.constraint_region.primitive_poses.append(pose.pose)
        pos_constraint.weight = 1.0

        constraint.position_constraints.append(pos_constraint)

        goal.request.goal_constraints.append(constraint)

        self.get_logger().info(f"Sending goal to {x}, {y}, {z}")

        send_goal_future = self.client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, send_goal_future)

        goal_handle = send_goal_future.result()

        if not goal_handle.accepted:
            self.get_logger().error("Goal rejected")
            return

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        self.get_logger().info("Motion complete")
        
    def add_environment(self):
        self.scene_client = self.create_client(
            ApplyPlanningScene, "/apply_planning_scene"
        )

        while not self.scene_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for planning scene...")

        scene = PlanningScene()
        scene.is_diff = True

        objects = []

        # TABLE
        table = CollisionObject()
        table.id = "table"
        table.header.frame_id = "base_link"

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = [1.0, 0.8, 0.05]

        pose = PoseStamped().pose
        pose.position.x = 0.5
        pose.position.y = 0.0
        pose.position.z = -0.025

        table.primitives.append(primitive)
        table.primitive_poses.append(pose)
        table.operation = CollisionObject.ADD

        objects.append(table)

        # PAN
        pan = CollisionObject()
        pan.id = "pan"
        pan.header.frame_id = "base_link"

        primitive2 = SolidPrimitive()
        primitive2.type = SolidPrimitive.BOX
        primitive2.dimensions = [0.2, 0.2, 0.05]

        pose2 = PoseStamped().pose
        pose2.position.x = 0.5
        pose2.position.y = -0.25
        pose2.position.z = 0.025

        pan.primitives.append(primitive2)
        pan.primitive_poses.append(pose2)
        pan.operation = CollisionObject.ADD

        objects.append(pan)

        # CONTAINER
        container = CollisionObject()
        container.id = "container"
        container.header.frame_id = "base_link"

        primitive3 = SolidPrimitive()
        primitive3.type = SolidPrimitive.BOX
        primitive3.dimensions = [0.08, 0.08, 0.1]

        pose3 = PoseStamped().pose
        pose3.position.x = 0.3
        pose3.position.y = 0.2
        pose3.position.z = 0.05

        container.primitives.append(primitive3)
        container.primitive_poses.append(pose3)
        container.operation = CollisionObject.ADD

        objects.append(container)

        scene.world.collision_objects = objects

        req = ApplyPlanningScene.Request()
        req.scene = scene

        future = self.scene_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)

        self.get_logger().info("Environment added")


    def move_to_container(self):
        self.get_logger().info("Moving to container")
        self.move_to_pose(0.3, 0.2, 0.15)

    def move_to_pan(self):
        self.get_logger().info("Moving to pan")
        self.move_to_pose(0.5, -0.25, 0.15)

    def move_home(self):
        self.get_logger().info("Moving home")
        self.move_to_pose(0.2, 0.0, 0.3)

    def run_task(self):
        self.move_to_container()
        time.sleep(1)
        self.move_to_pan()
        time.sleep(1)
        self.move_home()


def main():
    rclpy.init()
    node = MoveArm()

    node.run_task()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
