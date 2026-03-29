import rclpy
from rclpy.node import Node
from moveit_msgs.msg import CollisionObject, PlanningScene
from shape_msgs.msg import Mesh
from geometry_msgs.msg import Pose
from ament_index_python.packages import get_package_share_directory
import os
import trimesh

class SceneAdder(Node):
    def __init__(self):
        super().__init__('scene_adder')

        self.pub = self.create_publisher(PlanningScene, '/planning_scene', 10)

        pkg_path = get_package_share_directory('piper_task')

        self.container_mesh_path = os.path.join(pkg_path, 'meshes', 'container.stl')
        self.pan_mesh_path = os.path.join(pkg_path, 'meshes', 'pan.stl')

        self.timer = self.create_timer(2.0, self.add_objects)

    def load_mesh(self, path):
        mesh = trimesh.load(path)

        ros_mesh = Mesh()
        ros_mesh.vertices = [tuple(v) for v in mesh.vertices]
        ros_mesh.triangles = []

        for face in mesh.faces:
            ros_mesh.triangles.append(
                type('Triangle', (), {
                    'vertex_indices': face
                })()
            )

        return ros_mesh

    def add_objects(self):
        scene = PlanningScene()
        scene.is_diff = True

        objects = []

        # 🔴 Container
        container = CollisionObject()
        container.id = "container_5"
        container.header.frame_id = "base_link"

        container_mesh = self.load_mesh(self.container_mesh_path)

        pose = Pose()
        pose.position.x = 0.4
        pose.position.y = 0.3
        pose.position.z = 0.0

        container.meshes.append(container_mesh)
        container.mesh_poses.append(pose)
        container.operation = CollisionObject.ADD

        objects.append(container)

        # 🔵 Pan
        pan = CollisionObject()
        pan.id = "pan_2"
        pan.header.frame_id = "base_link"

        pan_mesh = self.load_mesh(self.pan_mesh_path)

        pose2 = Pose()
        pose2.position.x = 0.5
        pose2.position.y = -0.2
        pose2.position.z = 0.0

        pan.meshes.append(pan_mesh)
        pan.mesh_poses.append(pose2)
        pan.operation = CollisionObject.ADD

        objects.append(pan)

        scene.world.collision_objects = objects

        self.pub.publish(scene)
        self.get_logger().info("Meshes added")

def main():
    rclpy.init()
    node = SceneAdder()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
