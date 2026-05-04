#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import FSMState


class Drive_Square:
    def __init__(self):
        # Initialize movement message
        self.cmd_msg = Twist2DStamped()

        # This is used so robot does not start again and again
        self.is_moving = False

        # Initialize ROS node
        rospy.init_node('drive_square_node', anonymous=True)

        # Publisher and subscriber topics for my robot
        self.pub = rospy.Publisher('/mybota002822/car_cmd_switch_node/cmd',
                                   Twist2DStamped,
                                   queue_size=1)

        rospy.Subscriber('/mybota002822/fsm_node/mode',
                         FSMState,
                         self.fsm_callback,
                         queue_size=1)

        rospy.loginfo("Open loop square node started")

    # Robot only moves when lane following is selected from joystick app
    def fsm_callback(self, msg):
        rospy.loginfo("State: %s", msg.state)

        if msg.state == "NORMAL_JOYSTICK_CONTROL":
            self.stop_robot()

        elif msg.state == "LANE_FOLLOWING":
            if not self.is_moving:
                rospy.sleep(1)
                self.move_robot()

    # Sends zero velocity to stop the robot
    def stop_robot(self):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.0
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)

    # Move robot forward for selected time
    def move_forward(self, speed, duration):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = speed
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)

        rospy.loginfo("Moving forward")
        rospy.sleep(duration)

        self.stop_robot()
        rospy.sleep(0.3)

    # Turn robot left for selected time
    def turn_left(self, speed, duration):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.0
        self.cmd_msg.omega = speed
        self.pub.publish(self.cmd_msg)

        rospy.loginfo("Turning left")
        rospy.sleep(duration)

        self.stop_robot()
        rospy.sleep(0.3)

    # Robot drives in a square and then stops
    def move_robot(self):
        self.is_moving = True
        rospy.loginfo("Starting open loop square movement")

        # Speed values
        forward_speed = 0.25
        turn_speed = 3.0

        # Time values. You can tune these after testing.
        straight_time = 4.0
        turn_time = 0.55

        # Repeat 4 times to make square
        for side in range(4):
            rospy.loginfo("Side %d: forward", side + 1)
            self.move_forward(forward_speed, straight_time)

            rospy.loginfo("Corner %d: turn", side + 1)
            self.turn_left(turn_speed, turn_time)

        self.stop_robot()
        rospy.loginfo("Square movement completed")
        self.is_moving = False

    # Keep node running
    def run(self):
        rospy.spin()


if __name__ == '__main__':
    try:
        duckiebot_movement = Drive_Square()
        duckiebot_movement.run()
    except rospy.ROSInterruptException:
        pass
