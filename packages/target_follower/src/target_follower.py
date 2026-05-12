#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import AprilTagDetectionArray


class TargetFollower:
    def __init__(self):
        # Start ROS node
        rospy.init_node("target_follower_node", anonymous=True)

        # Stop robot safely when program closes
        rospy.on_shutdown(self.clean_shutdown)

        # Your Duckiebot name
        self.robot_name = "mybota002443"

        # Publisher: sends movement command to robot
        self.cmd_vel_pub = rospy.Publisher(
            "/" + self.robot_name + "/car_cmd_switch_node/cmd",
            Twist2DStamped,
            queue_size=1
        )

        # Subscriber: receives AprilTag detection data
        rospy.Subscriber(
            "/" + self.robot_name + "/apriltag_detector_node/detections",
            AprilTagDetectionArray,
            self.tag_callback,
            queue_size=1
        )

        # Control values
        self.seek_speed = 2.0          # speed for searching when no tag is found
        self.turn_gain = 3.0           # how strongly robot turns towards tag
        self.dead_zone = 0.05          # small centre area where robot stops turning
        self.max_turn_speed = 3.5      # maximum turning speed

        rospy.loginfo("Target follower node started for robot: %s", self.robot_name)

        # Keep node running
        rospy.spin()

    def tag_callback(self, msg):
        # This function runs whenever AprilTag data is received
        self.move_robot(msg.detections)

    def clean_shutdown(self):
        # Stop robot before shutting down
        rospy.loginfo("System shutting down. Stopping robot...")
        self.stop_robot()

    def stop_robot(self):
        # Send zero speed to stop robot
        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = 0.0
        cmd_msg.omega = 0.0
        self.cmd_vel_pub.publish(cmd_msg)

    def send_command(self, linear_speed, angular_speed):
        # Send movement command to robot
        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = linear_speed
        cmd_msg.omega = angular_speed
        self.cmd_vel_pub.publish(cmd_msg)

    def move_robot(self, detections):
        # Feature 1: Seek object
        # If no AprilTag is visible, robot rotates slowly and searches.
        if len(detections) == 0:
            rospy.loginfo("No tag found. Searching...")
            self.send_command(0.0, self.seek_speed)
            return

        # Feature 2: Look at object
        # Use first detected AprilTag.
        tag = detections[0]

        x = tag.transform.translation.x
        y = tag.transform.translation.y
        z = tag.transform.translation.z
        tag_id = tag.tag_id

        rospy.loginfo("Tag ID: %d | x: %.3f y: %.3f z: %.3f", tag_id, x, y, z)

        # x tells if tag is left or right from camera centre
        error = x

        # If tag is almost in centre, stop rotating
        if abs(error) < self.dead_zone:
            rospy.loginfo("Tag is near centre. Stopping rotation.")
            self.send_command(0.0, 0.0)
            return

        # P control: more error means more turning
        omega = -self.turn_gain * error

        # Limit angular speed
        if omega > self.max_turn_speed:
            omega = self.max_turn_speed
        elif omega < -self.max_turn_speed:
            omega = -self.max_turn_speed

        rospy.loginfo("Looking at tag. omega: %.3f", omega)

        # v = 0 because task only needs in-place rotation
        self.send_command(0.0, omega)


if __name__ == "__main__":
    try:
        TargetFollower()
    except rospy.ROSInterruptException:
        pass
