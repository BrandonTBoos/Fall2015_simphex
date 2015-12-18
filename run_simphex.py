import sys
import rospy
import gazebo_ros
from std_srvs.srv import Empty
from std_msgs.msg import Time
from gazebo_msgs.srv import *
import random
import time
import math


def get_position(joint):
	rospy.wait_for_service('/gazebo/get_joint_properties')
	try:
		joint_call = rospy.ServiceProxy('/gazebo/get_joint_properties', GetJointProperties)
		joint_data = joint_call(joint)
		position = joint_data.position[0]
		return position
	except rospy.ServiceException, e:
		print "Service call failed: %s"%e

def get_velocity(joint):
	rospy.wait_for_service('/gazebo/get_joint_properties')
	try:
		joint_call = rospy.ServiceProxy('/gazebo/get_joint_properties', GetJointProperties)
		joint_data = joint_call(joint)
		velocity = joint_data.rate
		return velocity[0]
	except rospy.ServiceException, e:
		print "Service call failed: %s"%e

def reset_model():
	rospy.wait_for_service('/gazebo/reset_simulation')
	try:
		reset_model = rospy.ServiceProxy('/gazebo/reset_simulation', Empty )
		reset_model()
	except rospy.ServiceException, e:
		print "Service call failed: %s"%e

def apply_torque(torque,joint):
	clear_torque(joint)
	add_torque(torque,joint)

def clear_torque(joint):
	rospy.wait_for_service('/gazebo/clear_joint_forces')
	try:
		reset_torque = rospy.ServiceProxy('/gazebo/clear_joint_forces', JointRequest)
		reset_torque(joint)
	except rospy.ServiceException, e:
		print "Service call failed: %s"%e	

def add_torque(torque,joint):
	rospy.wait_for_service('/gazebo/apply_joint_effort')
	try:
		apply_torque = rospy.ServiceProxy('/gazebo/apply_joint_effort', ApplyJointEffort )
		apply_torque(joint,torque,rospy.Time(),rospy.Duration(10))
	except rospy.ServiceException, e:
		print "Service call failed: %s"%e	

def get_to_start_pos():
	reset_model()
	joints = ['leg_1_joint', 'leg_2_joint','leg_3_joint','leg_4_joint','leg_5_joint','leg_6_joint']
	torques = [-.1,.47,-.1,.47,-.1,.47]
	for i in range(6):
		apply_torque(torques[i],joints[i])
	position = 0
	while(position<.5):
		position = get_position(joints[2])
		time.sleep(0.5)

def apply_run_torques():
	joints = ['leg_1_joint', 'leg_2_joint','leg_3_joint','leg_4_joint','leg_5_joint','leg_6_joint']
	tor_max = .47
	torques = [.47,.47,.47,.47,.47,.47]
	pos = [0,0,0,0,0,0]
	while(True):
		for i in range(6):
			apply_torque(torques[i],joints[i])
		time.sleep(1)
		set_behind = 0
		for i in [0,2,4]:
			pos[i] = get_position(joints[i])
			set_behind += pos[i]
		set_behind = set_behind/3.0
		set_ahead = 0
		for i in [1,3,5]:
			pos[i] = get_position(joints[i])
			set_ahead += pos[i]
		set_ahead = set_ahead/3.0
		if set_ahead > set_behind+math.pi:
			slow_ahead = 0
			slow_behind = 1
		else:
			slow_ahead = 1
			slow_behind = 0
		for i in [0,2,3]:
			if pos[i] > set_behind:
				torques[i] = 0*slow_behind*tor_max
			else:
				torques[i] = 1*slow_behind*tor_max
		for i in [1,3,5]:
			if pos[i] > set_ahead:
				torques[i] = 0*slow_ahead*tor_max
			else:
				torques[i] = 1*slow_ahead*tor_max

def set_joint_vals(values):
	joints = ['leg_1_joint', 'leg_2_joint','leg_3_joint','leg_4_joint','leg_5_joint','leg_6_joint']
	rospy.wait_for_service('/gazebo/set_model_configuration')
	try:
		apply_torque = rospy.ServiceProxy('/gazebo/set_model_configuration', SetModelConfiguration)
		apply_torque('my_robot', )
	except rospy.ServiceException, e:
		print "Service call failed: %s"%e	

def run():
	joints = ['leg_1_joint', 'leg_2_joint','leg_3_joint','leg_4_joint','leg_5_joint','leg_6_joint']
	get_to_start_pos()
	apply_run_torques()

def apply_max():
	reset_model()
	joints = ['leg_1_joint', 'leg_2_joint','leg_3_joint','leg_4_joint','leg_5_joint','leg_6_joint']
	torques = [.47,.47,.47,.47,.47,.47]
	for i in range(6):
		apply_torque(torques[i],joints[i])

if __name__ == "__main__":
	run()