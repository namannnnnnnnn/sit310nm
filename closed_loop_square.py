#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import FSMState
from duckietown_msgs.msg import WheelEncoderStamped
from duckietown_msgs.msg import WheelsCmdStamped


class ClosedLoopSquare:
    def __init__(self):
        rospy.init_node("closed_loop_square_node", anonymous=True)

        self.robot_name = "mybota002443"

        self.fsm_topic = "/" + self.robot_name + "/fsm_node/mode"
        self.left_encoder_topic = "/" + self.robot_name + "/left_wheel_encoder_node/tick"
        self.right_encoder_topic = "/" + self.robot_name + "/right_wheel_encoder_node/tick"
        self.wheel_cmd_topic = "/" + self.robot_name + "/wheels_driver_node/wheels_cmd"

        self.wheel_pub = rospy.Publisher(
            self.wheel_cmd_topic,
            WheelsCmdStamped,
            queue_size=1
        )

        rospy.Subscriber(self.fsm_topic, FSMState, self.fsm_callback, queue_size=1)
        rospy.Subscriber(self.left_encoder_topic, WheelEncoderStamped, self.left_encoder_callback, queue_size=1)
        rospy.Subscriber(self.right_encoder_topic, WheelEncoderStamped, self.right_encoder_callback, queue_size=1)

        self.left_tick = None
        self.right_tick = None
        self.start_left_tick = None
        self.start_right_tick = None

        self.active = False
        self.state = "IDLE"
        self.side_count = 0

        # Tune these values according to your robot
        self.forward_target_ticks = 650
        self.turn_target_ticks = 90

        # Direct wheel speeds
        self.forward_wheel_speed = 0.25
        self.turn_wheel_speed = 0.25

        rospy.Timer(rospy.Duration(0.05), self.control_loop)

        rospy.loginfo("Closed loop square node started")
        rospy.loginfo("Robot name: %s", self.robot_name)
        rospy.loginfo("Publishing wheel commands to: %s", self.wheel_cmd_topic)

    def left_encoder_callback(self, msg):
        self.left_tick = msg.data

    def right_encoder_callback(self, msg):
        self.right_tick = msg.data

    def fsm_callback(self, msg):
        rospy.loginfo("FSM State: %s", msg.state)

        if msg.state == "NORMAL_JOYSTICK_CONTROL":
            self.active = False
            self.state = "IDLE"
            self.stop_robot()

        elif msg.state == "LANE_FOLLOWING":
            if not self.active:
                rospy.loginfo("Starting closed-loop square movement")
                self.active = True
                self.side_count = 0
                self.start_move_straight()

    def publish_wheels(self, left_speed, right_speed):
        msg = WheelsCmdStamped()
        msg.header.stamp = rospy.Time.now()
        msg.vel_left = left_speed
        msg.vel_right = right_speed
        self.wheel_pub.publish(msg)

    def stop_robot(self):
        self.publish_wheels(0.0, 0.0)

    def reset_encoder_start(self):
        self.start_left_tick = self.left_tick
        self.start_right_tick = self.right_tick

    def get_average_tick_change(self):
        if self.left_tick is None or self.right_tick is None:
            return 0

        if self.start_left_tick is None or self.start_right_tick is None:
            return 0

        left_change = abs(self.left_tick - self.start_left_tick)
        right_change = abs(self.right_tick - self.start_right_tick)

        return (left_change + right_change) / 2.0

    def start_move_straight(self):
        if self.left_tick is None or self.right_tick is None:
            rospy.logwarn("Waiting for encoder data before moving straight")
            return

        self.reset_encoder_start()
        self.state = "MOVE_STRAIGHT"
        rospy.loginfo("Moving straight for side %d", self.side_count + 1)

    def start_rotate_in_place(self):
        if self.left_tick is None or self.right_tick is None:
            rospy.logwarn("Waiting for encoder data before rotating")
            return

        self.reset_encoder_start()
        self.state = "ROTATE"
        rospy.loginfo("Rotating 90 degrees")

    def control_loop(self, event):
        if not self.active:
            return

        if self.left_tick is None or self.right_tick is None:
            self.stop_robot()
            rospy.logwarn("No encoder data received yet")
            return

        tick_change = self.get_average_tick_change()

        if self.state == "MOVE_STRAIGHT":
            if tick_change < self.forward_target_ticks:
                self.publish_wheels(self.forward_wheel_speed, self.forward_wheel_speed)
            else:
                self.stop_robot()
                rospy.loginfo("Straight movement completed. Tick change: %.2f", tick_change)
                rospy.sleep(0.3)
                self.start_rotate_in_place()

        elif self.state == "ROTATE":
            if tick_change < self.turn_target_ticks:
                self.publish_wheels(self.turn_wheel_speed, -self.turn_wheel_speed)
            else:
                self.stop_robot()
                rospy.loginfo("Rotation completed. Tick change: %.2f", tick_change)
                rospy.sleep(0.3)

                self.side_count += 1

                if self.side_count < 4:
                    self.start_move_straight()
                else:
                    self.state = "DONE"
                    self.active = False
                    self.stop_robot()
                    rospy.loginfo("Closed-loop square completed")

    def run(self):
        rospy.spin()


if __name__ == "__main__":
    try:
        node = ClosedLoopSquare()
        node.run()
    except rospy.ROSInterruptException:
        pass
