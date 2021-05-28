#!/usr/bin/env python
import rospy
from ackermann_msgs.msg import AckermannDriveStamped
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
import datetime as dt
import math

class Regions():
	def __init__(self,):
		self.ack_msg = AckermannDriveStamped()
		self.ack_pub = rospy.Publisher('/vesc/sns_msg', AckermannDriveStamped , queue_size=1000)
		self.scan_sub = rospy.Subscriber('scan', LaserScan, self.rplidarCallback)
		self.timeArr = []
		self.boolean = True

	def rplidarCallback(self, data):
		arr = []
		arr.insert(0, min(data.ranges[270:306])) #Right 
		arr.insert(1, min(data.ranges[306:342])) #FRight
		arr.insert(2, min(min(data.ranges[0:18]), min(data.ranges[341:360]))) #Front
		arr.insert(3, min(data.ranges[18:54])) #FLeft
		arr.insert(4, min(data.ranges[54:90])) #Left

		angle = data.ranges.index(min(arr))

		if(angle <= 89): 
			radian = -(angle*(math.pi/180))
		else:
			radian = (359-angle)*(math.pi/180)

		if((arr[2] < 0.5) and self.boolean == True): #front
			self.ack_msg.drive.speed = 0
			self.boolean = False
		elif(self.boolean == False):
			print("back")
			self.ack_msg.drive.speed = -0.5
			self.ack_msg.drive.steering_angle = -radian
			self.timeArr.append(dt.datetime.now())
			time = self.timeArr[len(self.timeArr)-1]-self.timeArr[0]
			time = time.microseconds/float(1000000) + (time.seconds + time.days * 24 * 3600)
			if(time >= 3.0):
				self.ack_msg.drive.speed = 0
				self.boolean = True
				print("stop")
#			print(self.timeArr)
		elif((min(arr) == arr[0]) and (arr[0] < 0.75) and self.boolean == True): #right
			self.ack_msg.drive.speed = 0.7
			self.ack_msg.drive.steering_angle = 0
			self.timeArr = []
			print("right")
		elif((min(arr) == arr[1]) and (arr[1] < 0.75) and self.boolean == True): #f_right
			self.ack_msg.drive.speed = 0.7
			self.ack_msg.drive.steering_angle = 0
			self.timeArr = []
			print("fright")
		elif((min(arr) == arr[3]) and (arr[3] < 0.75) and self.boolean == True): #f_left
			self.ack_msg.drive.speed = 0.7
			self.ack_msg.drive.steering_angle = 0
			self.timeArr = []
			print("fleft")
		elif((min(arr) == arr[4]) and (arr[4] < 0.75) and self.boolean == True): #left
			self.ack_msg.drive.speed = 0.7
			self.ack_msg.drive.steering_angle = 0
			self.timeArr = []
			print("left")
		else: # Straight
			self.ack_msg.drive.speed = 0.7
			self.ack_msg.drive.steering_angle = 0
			self.timeArr = []

	def pub_driver(self):
#		self.ack_msg.drive.speed = 0.7
		self.ack_pub.publish(self.ack_msg)

if __name__ == "__main__":
	try:
		rospy.init_node('car_driver_py')
		regions = Regions()
		while not rospy.is_shutdown():
			regions.pub_driver()
		rospy.spin()
	except rospy.ROSInterrupException:
		pass

