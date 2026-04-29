#!/usr/bin/env python3

import rospy
import time
from duckietown_msgs.msg import Twist2DStamped

class SquareNode:

    def __init__(self):
        self.node_name = "open_loop_square_node"
        rospy.init_node(self.node_name)

        self.robot_name = rospy.get_namespace().strip("/")
        topic = f"/{self.robot_name}/car_cmd_switch_node/cmd"

        self.pub = rospy.Publisher(topic, Twist2DStamped, queue_size=1)
        rospy.sleep(2)

    def stop(self):
        msg = Twist2DStamped()
        msg.v = 0.0
        msg.omega = 0.0
        self.pub.publish(msg)
        rospy.sleep(1)

    def move(self, v, omega, duration):
        msg = Twist2DStamped()
        msg.v = v
        msg.omega = omega

        start = time.time()

        while time.time() - start < duration and not rospy.is_shutdown():
            self.pub.publish(msg)
            rospy.sleep(0.1)

        self.stop()

    def run(self):
        forward_time = 3.3
        turn_time = 1.25

        for i in range(4):
            rospy.loginfo(f"Side {i+1}")

            # Move forward
            self.move(0.3, 0.0, forward_time)

            # Turn
            self.move(0.0, 2.5, turn_time)

        self.stop()
        rospy.loginfo("Square Completed")


if __name__ == "__main__":
    node = SquareNode()
    node.run()
