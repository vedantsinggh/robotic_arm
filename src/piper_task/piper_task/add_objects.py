import rclpy
from rclpy.node import Node

from moveit_msgs.msg import CollisionObject, PlanningScene
from moveit_msgs.srv import ApplyPlanningScene
from shape_msgs.msg import Mesh, MeshTriangle
from geometry_msgs.msg import Pose, Point

from ament_index_python.packages import get_package_share_directory

import os
import trimesh


class SceneAdder(Node):
    def __init__(self):
        super().__init__('scene_adder')

        # ✅ Service client (correct way)
        self.client = self.create_client(ApplyPlanningScene, '/apply_planning_scene')

        pkg_path = get_package_share_directory('piper_task')

        self.container_mesh_path = os.path.join(pkg_path, 'meshes', 'container.stl')
        self.pan_mesh_path = os.path.join(pkg_path, 'meshes', 'pan.stl')

        #self.timer = self.create_timer(2.0, self.add_objects)

    def load_mesh(self, path):
        if not os.path.exists(path):
            self.get_logger().error(f"Mesh not found: {path}")
            return None

        mesh = trimesh.load(path)

        # 🔧 Uncomment if your STL is in mm
        mesh.apply_scale(0.001)

        ros_mesh = Mesh()

        # vertices
        for v in mesh.vertices:
            p = Point()
            p.x = float(v[0])
            p.y = float(v[1])
            p.z = float(v[2])
            ros_mesh.vertices.append(p)

        # triangles
        for face in mesh.faces:
            tri = MeshTriangle()
            tri.vertex_indices = [int(face[0]), int(face[1]), int(face[2])]
            ros_mesh.triangles.append(tri)

        return ros_mesh

    def add_objects(self):
        # Wait for MoveIt service
        if not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /apply_planning_scene service...')
            return

        scene = PlanningScene()
        scene.is_diff = True

        objects = []

        # 🔴 Container
        container_mesh = self.load_mesh(self.container_mesh_path)
        if container_mesh:
            container = CollisionObject()
            container.id = "container_5"
            container.header.frame_id = "base_link"

            pose = Pose()
            pose.position.x = 0.4
            pose.position.y = 0.3
            pose.position.z = 0.0
            pose.orientation.w = 1.0

            container.meshes.append(container_mesh)
            container.mesh_poses.append(pose)
            container.operation = CollisionObject.ADD

            objects.append(container)

        # 🔵 Pan
        pan_mesh = self.load_mesh(self.pan_mesh_path)
        if pan_mesh:
            pan = CollisionObject()
            pan.id = "pan_2"
            pan.header.frame_id = "base_link"

            pose2 = Pose()
            pose2.position.x = 0.5
            pose2.position.y = -0.2
            pose2.position.z = 0.0
            pose2.orientation.w = 1.0

            pan.meshes.append(pan_mesh)
            pan.mesh_poses.append(pose2)
            pan.operation = CollisionObject.ADD

            objects.append(pan)

        scene.world.collision_objects = objects

        # ✅ Call service
        req = ApplyPlanningScene.Request()
        req.scene = scene

        self.client.call_async(req)

        self.get_logger().info("Meshes applied to MoveIt planning scene")


#def main():
    #rclpy.init()
    #node = SceneAdder()
    #rclpy.spin(node)

def main():
    rclpy.init()
    node = SceneAdder()

    node.add_objects()   # run once

    node.get_logger().info("Done. Shutting down.")
    rclpy.shutdown()


if __name__ == '__main__':
    main()
