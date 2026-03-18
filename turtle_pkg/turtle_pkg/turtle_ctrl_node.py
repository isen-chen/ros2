import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class TurtleCtrlNode(Node):

    def __init__(self):
        super().__init__('turtle_ctrl_node')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.timer_period = 0.1
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.cmd_count = 0
        self.max_cmds = 100
        self.get_logger().info('Turtle Control Node has been started')

    def timer_callback(self):
        twist = Twist()
        
        if self.cmd_count < self.max_cmds:
            twist.linear.x = 0.5
            twist.angular.z = 0.5
            self.cmd_count += 1
            if self.cmd_count == 1:
                self.get_logger().info('Sending velocity commands...')
        else:
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            if self.cmd_count == self.max_cmds:
                self.get_logger().info('Velocity commands stopped')
                self.cmd_count += 1
        
        self.publisher_.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleCtrlNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()