#!/usr/bin/env python3

import rospy
import cv2
import numpy as np
from cv_bridge import CvBridge
from sensor_msgs.msg import CompressedImage


class LaneDetector:
    def __init__(self):
        rospy.init_node("my_lane_detector", anonymous=True)

        self.bridge = CvBridge()

        # Topic from provided some_lane_images.bag file
        # If your rosbag info shows different topic, change this line.
        self.image_topic = "/akandb/camera_node/image/compressed"

        self.sub = rospy.Subscriber(
            self.image_topic,
            CompressedImage,
            self.image_callback,
            queue_size=1
        )

        rospy.loginfo("Lane detector node started")
        rospy.loginfo("Subscribed to: %s", self.image_topic)

    def draw_lines(self, image, lines, color):
        output = image.copy()

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]

                cv2.line(output, (x1, y1), (x2, y2), color, 3, cv2.LINE_AA)
                cv2.circle(output, (x1, y1), 3, (0, 255, 0), -1)
                cv2.circle(output, (x2, y2), 3, (0, 0, 255), -1)

        return output

    def image_callback(self, msg):
        rospy.loginfo("Image received")

        # Convert ROS compressed image to OpenCV BGR image
        img = self.bridge.compressed_imgmsg_to_cv2(msg, "bgr8")

        # 1. Crop image so mainly road is visible
        cropped = img[260:480, 0:640]

        # 2. Convert cropped image to HSV colour space
        hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)

        # 3. White colour filtering
        lower_white = np.array([0, 0, 160])
        upper_white = np.array([180, 80, 255])

        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        white_filtered = cv2.bitwise_and(cropped, cropped, mask=white_mask)

        # 4. Yellow colour filtering
        lower_yellow = np.array([15, 60, 80])
        upper_yellow = np.array([40, 255, 255])

        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        yellow_filtered = cv2.bitwise_and(cropped, cropped, mask=yellow_mask)

        # 5. Clean masks using erosion and dilation
        kernel = np.ones((5, 5), np.uint8)

        white_mask_clean = cv2.erode(white_mask, kernel, iterations=1)
        white_mask_clean = cv2.dilate(white_mask_clean, kernel, iterations=1)

        yellow_mask_clean = cv2.erode(yellow_mask, kernel, iterations=1)
        yellow_mask_clean = cv2.dilate(yellow_mask_clean, kernel, iterations=1)

        # 6. Canny edge detection
        gray_cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        canny_edges = cv2.Canny(gray_cropped, 80, 180)

        white_edges = cv2.Canny(white_mask_clean, 80, 180)
        yellow_edges = cv2.Canny(yellow_mask_clean, 80, 180)

        # 7. Hough Transform on white filtered image
        white_lines = cv2.HoughLinesP(
            white_edges,
            rho=1,
            theta=np.pi / 180,
            threshold=25,
            minLineLength=20,
            maxLineGap=15
        )

        # 8. Hough Transform on yellow filtered image
        yellow_lines = cv2.HoughLinesP(
            yellow_edges,
            rho=1,
            theta=np.pi / 180,
            threshold=20,
            minLineLength=15,
            maxLineGap=15
        )

        # 9. Draw both Hough Transform lines on cropped image
        hough_output = cropped.copy()

        # Blue lines = detected white lane lines
        hough_output = self.draw_lines(hough_output, white_lines, (255, 0, 0))

        # Red lines = detected yellow dashed lines
        hough_output = self.draw_lines(hough_output, yellow_lines, (0, 0, 255))

        # 10. Show output windows
        cv2.imshow("1 Cropped Road Image", cropped)
        cv2.imshow("2 White Filtered Image", white_filtered)
        cv2.imshow("3 Yellow Filtered Image", yellow_filtered)
        cv2.imshow("4 Canny Edge Image", canny_edges)
        cv2.imshow("5 Hough Lines Output", hough_output)

        cv2.waitKey(1)

    def run(self):
        rospy.spin()


if __name__ == "__main__":
    try:
        detector = LaneDetector()
        detector.run()
    except rospy.ROSInterruptException:
        pass
    finally:
        cv2.destroyAllWindows()
