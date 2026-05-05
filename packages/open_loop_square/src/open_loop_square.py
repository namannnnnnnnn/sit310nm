#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped


class OpenLoopSquare:
    def __init__(self):
        # Start ROS node
        rospy.init_node("open_loop_square_direct_node", anonymous=True)

        # Robot command topic
        self.cmd_topic = "/mybota002822/car_cmd_switch_node/cmd"

        # Publisher sends speed command to robot
        self.pub = rospy.Publisher(self.cmd_topic, Twist2DStamped, queue_size=1)

        # Movement message
        self.cmd_msg = Twist2DStamped()

        # Wait so publisher can connect properly
        rospy.sleep(2)

        rospy.loginfo("Direct open loop square code started")
        rospy.loginfo("Publishing to: %s", self.cmd_topic)

    def stop_robot(self):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.0
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)

    def move_forward(self, speed, duration):
        rospy.loginfo("Moving forward")

        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = speed
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)

        rospy.sleep(duration)

        self.stop_robot()
        rospy.sleep(0.5)

    def turn_left(self, speed, duration):
        rospy.loginfo("Turning left")

        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.0
        self.cmd_msg.omega = speed
        self.pub.publish(self.cmd_msg)

        rospy.sleep(duration)

        self.stop_robot()
        rospy.sleep(0.5)

    def run_square(self):
        rospy.loginfo("Starting square movement")

        # Tune these values after testing
        forward_speed = 0.25
        turn_speed = 3.0

        # Approx values for 1 metre and 90 degree turn
        straight_time = 4.0
        turn_time = 0.55

        # Make 4 sides of square
        for side in range(4):
            rospy.loginfo("Side %d", side + 1)
            self.move_forward(forward_speed, straight_time)

            rospy.loginfo("Turn %d", side + 1)
            self.turn_left(turn_speed, turn_time)

        self.stop_robot()
        rospy.loginfo("Square completed")


if __name__ == "__main__":
    try:
        robot = OpenLoopSquare()
        robot.run_square()
    except rospy.ROSInterruptException:
        pass
