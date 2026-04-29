#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import FSMState


class DriveSquare:

    def __init__(self):
        # message object
        self.cmd_msg = Twist2DStamped()
        self.is_moving = False

        # initialize node
        rospy.init_node('drive_square_node', anonymous=True)

        # CHANGE robot name if different
        self.robot_name = "mybota002822"

        # publisher
        self.pub = rospy.Publisher(
            f"/{self.robot_name}/car_cmd_switch_node/cmd",
            Twist2DStamped,
            queue_size=1
        )

        # subscriber
        rospy.Subscriber(
            f"/{self.robot_name}/fsm_node/mode",
            FSMState,
            self.fsm_callback,
            queue_size=1
        )

    def fsm_callback(self, msg):
        rospy.loginfo("State: %s", msg.state)

        if msg.state == "NORMAL_JOYSTICK_CONTROL":
            self.stop_robot()
            self.is_moving = False

        elif msg.state == "LANE_FOLLOWING":
            if not self.is_moving:
                self.is_moving = True
                rospy.sleep(1)
                self.move_robot()
                self.is_moving = False

    def stop_robot(self):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.0
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)

    def move_robot(self):

        # you can adjust these values
        forward_speed = 0.4
        forward_time = 3.0   # increase/decrease for 1 meter

        turn_speed = 3.0
        turn_time = 1.2      # adjust for 90 degree

        for i in range(4):

            rospy.loginfo("Moving forward")

            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = forward_speed
            self.cmd_msg.omega = 0.0
            self.pub.publish(self.cmd_msg)
            rospy.sleep(forward_time)

            self.stop_robot()
            rospy.sleep(0.5)

            rospy.loginfo("Turning")

            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = 0.0
            self.cmd_msg.omega = turn_speed
            self.pub.publish(self.cmd_msg)
            rospy.sleep(turn_time)

            self.stop_robot()
            rospy.sleep(0.5)

        self.stop_robot()
        rospy.loginfo("Square completed")

    def run(self):
        rospy.spin()


if __name__ == '__main__':
    try:
        node = DriveSquare()
        node.run()
    except rospy.ROSInterruptException:
        pass
