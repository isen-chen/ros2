import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton)
from PyQt5.QtCore import QTimer, Qt
import sys


class TurtleAdvceCtrlNode(Node):

    def __init__(self, gui_callback):
        super().__init__('turtle_advce_ctrl_node')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscriber_ = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.gui_callback = gui_callback
        self.get_logger().info('Turtle Advanced Control Node has been started')

    def pose_callback(self, msg):
        if self.gui_callback:
            self.gui_callback(msg)


class TurtleControllerWindow(QMainWindow):

    def __init__(self, node):
        super().__init__()
        self.node = node
        self.setWindowTitle('小乌龟控制器')
        self.setGeometry(100, 100, 600, 500)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        self.create_widgets()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.publish_velocity)
        self.is_sending = False

    def create_widgets(self):
        linear_layout = QHBoxLayout()
        self.linear_label = QLabel('线速度')
        self.linear_label.setStyleSheet('font-size: 24px;')
        self.linear_input = QLineEdit('0.0')
        self.linear_input.setStyleSheet('font-size: 24px; padding: 5px;')
        linear_layout.addWidget(self.linear_label)
        linear_layout.addWidget(self.linear_input)
        self.layout.addLayout(linear_layout)
        
        angular_layout = QHBoxLayout()
        self.angular_label = QLabel('角速度')
        self.angular_label.setStyleSheet('font-size: 24px;')
        self.angular_input = QLineEdit('0.0')
        self.angular_input.setStyleSheet('font-size: 24px; padding: 5px;')
        angular_layout.addWidget(self.angular_label)
        angular_layout.addWidget(self.angular_input)
        self.layout.addLayout(angular_layout)
        
        self.x_label = self.create_status_label('当前X坐标', '0.0')
        self.layout.addWidget(self.x_label)
        
        self.y_label = self.create_status_label('当前Y坐标', '0.0')
        self.layout.addWidget(self.y_label)
        
        self.linear_vel_label = self.create_status_label('当前线速度', '0.0')
        self.layout.addWidget(self.linear_vel_label)
        
        self.angular_vel_label = self.create_status_label('当前角速度', '0.0')
        self.layout.addWidget(self.angular_vel_label)
        
        self.theta_label = self.create_status_label('当前角度', '0.0')
        self.layout.addWidget(self.theta_label)
        
        self.send_button = QPushButton('发送')
        self.send_button.setStyleSheet('font-size: 32px; padding: 15px;')
        self.send_button.clicked.connect(self.toggle_send)
        self.layout.addWidget(self.send_button)
        
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        self.status_label = QLabel('')
        self.status_label.setStyleSheet('color: red;')
        footer_layout.addWidget(self.status_label)
        self.layout.addLayout(footer_layout)

    def create_status_label(self, text, value):
        layout = QHBoxLayout()
        label = QLabel(text)
        label.setStyleSheet('font-size: 24px;')
        value_label = QLabel(value)
        value_label.setStyleSheet('font-size: 24px;')
        layout.addWidget(label)
        layout.addWidget(value_label)
        
        container = QWidget()
        container.setLayout(layout)
        container.value_label = value_label
        
        return container

    def update_pose(self, msg):
        self.x_label.value_label.setText(f'{msg.x:.6f}')
        self.y_label.value_label.setText(f'{msg.y:.6f}')
        self.linear_vel_label.value_label.setText(f'{msg.linear_velocity:.6f}')
        self.angular_vel_label.value_label.setText(f'{msg.angular_velocity:.6f}')
        self.theta_label.value_label.setText(f'{msg.theta:.6f}')

    def toggle_send(self):
        if self.is_sending:
            self.stop_sending()
        else:
            self.start_sending()

    def start_sending(self):
        self.is_sending = True
        self.send_button.setText('停止')
        self.send_button.setStyleSheet('font-size: 32px; padding: 15px; background-color: #ff6666;')
        self.timer.start(100)
        self.node.get_logger().info('Sending velocity commands...')

    def stop_sending(self):
        self.is_sending = False
        self.send_button.setText('发送')
        self.send_button.setStyleSheet('font-size: 32px; padding: 15px;')
        self.timer.stop()
        
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = 0.0
        self.node.publisher_.publish(twist)
        self.node.get_logger().info('Velocity commands stopped')

    def publish_velocity(self):
        try:
            linear_x = float(self.linear_input.text())
            angular_z = float(self.angular_input.text())
            
            twist = Twist()
            twist.linear.x = linear_x
            twist.angular.z = angular_z
            self.node.publisher_.publish(twist)
        except ValueError:
            pass


def main(args=None):
    rclpy.init(args=args)
    
    app = QApplication(sys.argv)
    
    node = None
    window = None
    
    try:
        window = TurtleControllerWindow(None)
        node = TurtleAdvceCtrlNode(window.update_pose)
        window.node = node
        window.show()
        
        ros_timer = QTimer()
        ros_timer.timeout.connect(lambda: rclpy.spin_once(node, timeout_sec=0.01))
        ros_timer.start(10)
        
        app.exec_()
    except KeyboardInterrupt:
        pass
    finally:
        if node:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()