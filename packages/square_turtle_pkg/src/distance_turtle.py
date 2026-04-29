#!/usr/bin/env python3

import rospy
from turtlesim.msg import Pose
import math

prev_x = None
prev_y = None
total_distance = 0.0

def callback(data):
    global prev_x, prev_y, total_distance

    if prev_x is None:
        prev_x = data.x
        prev_y = data.y
        return

    # calculate distance between points
    distance = math.sqrt((data.x - prev_x)**2 + (data.y - prev_y)**2)

    total_distance += distance

    prev_x = data.x
    prev_y = data.y

    rospy.loginfo("Total Distance Travelled: %.2f", total_distance)

def listener():
    rospy.init_node('distance_turtle_node', anonymous=True)
    rospy.Subscriber('/turtle1/pose', Pose, callback)
    rospy.spin()

if __name__ == '__main__':
    listener()
