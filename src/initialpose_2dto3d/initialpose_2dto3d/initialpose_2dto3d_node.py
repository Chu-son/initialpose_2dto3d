import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseStamped
import math

from .core.heightmap import HeightMapHandler

class InitialPose2DTo3DNode(Node):
    def __init__(self):
        super().__init__('initialpose_2dto3d_node')

        # 1. Declare Parameters
        self.declare_parameter('input_topic', '/initialpose_2d')
        self.declare_parameter('output_topic', '/initialpose')
        self.declare_parameter('map_yaml_path', '')
        self.declare_parameter('heightmap_path', '')
        self.declare_parameter('default_z', 0.0)

        # 2. Get Parameter Values
        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value
        map_yaml_path = self.get_parameter('map_yaml_path').value
        heightmap_path = self.get_parameter('heightmap_path').value
        default_z = self.get_parameter('default_z').value

        # 3. Initialize Core HeightMap Handler
        self.heightmap_handler = HeightMapHandler(
            map_yaml_path=map_yaml_path,
            heightmap_path=heightmap_path,
            default_z=default_z,
            logger=self.get_logger()
        )

        # 4. Setup QoS (matching RViz usual settings for /initialpose)
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE, # Or TRANSIENT_LOCAL if needed
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # 5. Initialize Pub/Sub
        self.sub = self.create_subscription(
            PoseWithCovarianceStamped,
            input_topic,
            self.callback,
            qos_profile
        )
        self.pub = self.create_publisher(
            PoseStamped,
            output_topic,
            qos_profile
        )

        self.get_logger().info(f"Node started. Subscribing to {input_topic}, publishing to {output_topic}")

    def callback(self, msg: PoseWithCovarianceStamped):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        
        # Get Z from heightmap
        z = self.heightmap_handler.get_z_at(x, y)
        
        # Reset Roll/Pitch while keeping Yaw
        # Formula for Yaw from Quaternion: atan2(2(wz + xy), 1 - 2(y^2 + z^2))
        q = msg.pose.pose.orientation
        yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        
        # New Quaternion with Roll=0, Pitch=0, Yaw=yaw
        # qx = 0, qy = 0, qz = sin(yaw/2), qw = cos(yaw/2)
        half_yaw = yaw * 0.5
        new_q_z = math.sin(half_yaw)
        new_q_w = math.cos(half_yaw)

        # Construct PoseStamped
        out_msg = PoseStamped()
        out_msg.header = msg.header
        out_msg.pose.position.x = x
        out_msg.pose.position.y = y
        out_msg.pose.position.z = z
        out_msg.pose.orientation.x = 0.0
        out_msg.pose.orientation.y = 0.0
        out_msg.pose.orientation.z = new_q_z
        out_msg.pose.orientation.w = new_q_w

        self.pub.publish(out_msg)
        self.get_logger().info(f"Published 3D Pose: x={x:.2f}, y={y:.2f}, z={z:.2f} (Yaw: {yaw:.2f} rad)")

def main(args=None):
    rclpy.init(args=args)
    node = InitialPose2DTo3DNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
