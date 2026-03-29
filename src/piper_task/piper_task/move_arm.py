import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, PositionConstraint
from geometry_msgs.msg import PoseStamped
from shape_msgs.msg import SolidPrimitive


class MoveArm(Node):
    def __init__(self):
        super().__init__('move_arm')

        self.client = ActionClient(self, MoveGroup, '/move_action')

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


def main():
    rclpy.init()
    node = MoveArm()

    node.move_to_pose(0.2, 0.0, 0.2)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
