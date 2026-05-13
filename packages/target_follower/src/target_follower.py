#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import AprilTagDetectionArray


class TargetFollower:
    def __init__(self):
        rospy.init_node("target_follower_node", anonymous=True)

        rospy.on_shutdown(self.clean_shutdown)

        # Robot name
        self.robot_name = "mybota002443"

        # Publisher for robot movement
        self.cmd_vel_pub = rospy.Publisher(
            "/" + self.robot_name + "/car_cmd_switch_node/cmd",
            Twist2DStamped,
            queue_size=1
        )

        # Subscriber for AprilTag detection
        rospy.Subscriber(
            "/" + self.robot_name + "/apriltag_detector_node/detections",
            AprilTagDetectionArray,
            self.tag_callback,
            queue_size=1
        )

        # Target following values
        self.target_distance = 0.35      # robot will try to keep this distance from tag
        self.distance_dead_zone = 0.05   # no forward/backward movement inside this range

        # Linear movement values
        self.linear_gain = 0.6
        self.max_linear_speed = 0.25
        self.min_linear_speed = 0.08

        # Rotation values
        self.turn_gain = 3.0
        self.center_dead_zone = 0.04
        self.max_turn_speed = 3.0
        self.min_turn_speed = 0.4

        rospy.loginfo("SIT310 5.2C Target Following node started")
        rospy.loginfo("Robot name: %s", self.robot_name)

        rospy.spin()

    def tag_callback(self, msg):
        self.move_robot(msg.detections)

    def clean_shutdown(self):
        rospy.loginfo("Shutting down. Stopping robot...")
        self.stop_robot()

    def stop_robot(self):
        self.send_command(0.0, 0.0)

    def send_command(self, linear_speed, angular_speed):
        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = linear_speed
        cmd_msg.omega = angular_speed
        self.cmd_vel_pub.publish(cmd_msg)

    def limit_value(self, value, max_value):
        if value > max_value:
            return max_value
        if value < -max_value:
            return -max_value
        return value

    def add_minimum_speed(self, value, min_value):
        if value > 0 and value < min_value:
            return min_value
        if value < 0 and value > -min_value:
            return -min_value
        return value

    def move_robot(self, detections):
        # In Task 5.2C, seek behaviour is not needed.
        # If no tag is detected, robot should stay stationary.
        if len(detections) == 0:
            rospy.loginfo("No AprilTag detected. Robot stopped.")
            self.stop_robot()
            return

        # Use first detected AprilTag
        tag = detections[0]

        x = tag.transform.translation.x
        y = tag.transform.translation.y
        z = tag.transform.translation.z
        tag_id = tag.tag_id

        rospy.loginfo("Tag ID: %d | x: %.3f y: %.3f z: %.3f", tag_id, x, y, z)

        # -----------------------------
        # 1. Rotation control
        # -----------------------------
        # x value tells if tag is left or right.
        # Robot rotates to keep the tag in the centre.
        turn_error = x

        if abs(turn_error) < self.center_dead_zone:
            omega = 0.0
        else:
            omega = -self.turn_gain * turn_error
            omega = self.limit_value(omega, self.max_turn_speed)
            omega = self.add_minimum_speed(omega, self.min_turn_speed)

        # -----------------------------
        # 2. Distance control
        # -----------------------------
        # z value gives distance from camera to tag.
        # If z is bigger than target distance, robot moves forward.
        # If z is smaller than target distance, robot moves backward slowly.
        distance_error = z - self.target_distance

        if abs(distance_error) < self.distance_dead_zone:
            v = 0.0
        else:
            v = self.linear_gain * distance_error
            v = self.limit_value(v, self.max_linear_speed)
            v = self.add_minimum_speed(v, self.min_linear_speed)

        rospy.loginfo("Command | v: %.3f omega: %.3f", v, omega)

        self.send_command(v, omega)


if __name__ == "__main__":
    try:
        TargetFollower()
    except rospy.ROSInterruptException:
        pass
