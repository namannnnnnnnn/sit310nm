#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist

def move_square():
    rospy.init_node('square_turtle_node', anonymous=True)
    pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)
    rate = rospy.Rate(1)

    rospy.loginfo("Turtles are great at drawing squares!")

    move_cmd = Twist()

    while not rospy.is_shutdown():
        move_cmd.linear.x = 2.0
        move_cmd.angular.z = 0.0
        for i in range(2):
            pub.publish(move_cmd)
            rate.sleep()

        move_cmd.linear.x = 0.0
        move_cmd.angular.z = 0.0
        pub.publish(move_cmd)
        rate.sleep()

        move_cmd.linear.x = 0.0
        move_cmd.angular.z = 1.57
        for i in range(1):
            pub.publish(move_cmd)
            rate.sleep()

        move_cmd.linear.x = 0.0
        move_cmd.angular.z = 0.0
        pub.publish(move_cmd)
        rate.sleep()

if __name__ == '__main__':
    try:
        move_square()
    except rospy.ROSInterruptException:
        pass
