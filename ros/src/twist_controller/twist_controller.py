
GAS_DENSITY = 2.858
ONE_MPH = 0.44704

import rospy
from pid import PID
from yaw_controller import YawController
from lowpass import LowPassFilter


class Controller(object):
    def __init__(self, **kwargs):
        # TODO: Implement
        # Fixed parameters

        self.vehicle_mass = kwargs['vehicle_mass']
        self.fuel_capacity = kwargs['fuel_capacity']
        self.brake_deadband = kwargs['brake_deadband']
        self.decel_limit = kwargs['decel_limit']
        self.accel_limit = kwargs['accel_limit']
        self.wheel_radius = kwargs['wheel_radius']
        self.wheel_base = kwargs['wheel_base']
        self.steer_ratio = kwargs['steer_ratio']
        self.max_lat_accel = kwargs['max_lat_accel']
        self.max_steer_angle = kwargs['max_steer_angle']

        # To be Updated in each cycle
        self.twist_command = None
        self.current_velocity = None
        self.enabled = True
        self.sample_time = 1/50 # initial value, gets updated in loop


        self.speed_PID = PID(0.2, 0.01, 0.05, mn = self.decel_limit, mx = self.accel_limit) # Dummy values
        self.steer_PID = PID(0.2, 0.0000001, 0.5, mn = -self.max_steer_angle, mx = self.max_steer_angle) # To be adjusted

        # initial control values	
        # self.steer = 0.0

        # To use the yaw_controller, activate the code below
        '''
        self.yaw_ctrl = YawController(self.wheel_base,
                                      self.steer_ratio,
                                      2.0,
                                      self.max_lat_accel,
                                      self.max_steer_angle) # Set the min_speed as 0

        self.LPF_angle = LowPassFilter(0.90, 1.0)
        '''
        # self.LPF_velocity = LowPassFilter(0.90, 1.0)
        self.LPF_target_v = LowPassFilter(0.90, 1.0)


    def get_speed_control_vector(self, speed_command):
        #default control behavior, don't do anything
        throttle = 0.0
        brake = 0.0

        if speed_command > 0.01:
            throttle = max(min(speed_command, 1.0), 0.0)
            brake = 0.0
        elif speed_command < 0.0:
            throttle = speed_command
            brake = (self.vehicle_mass + self.fuel_capacity * GAS_DENSITY) * min(abs(speed_command), abs(self.decel_limit)) * self.wheel_radius
        return throttle, brake

    def control(self, target_v, yaw_angle, actual_v, cte_value, dbw_status):
        # TODO: Change the arg, kwarg list to suit your needs
        # If we drive slower than the target sppeed, we push the gas pedal (throttle), othwise not
        # actual_v = self.LPF_velocity.filt(actual_v)
        target_v = self.LPF_target_v.filt(target_v)
        speed_error = target_v - actual_v
        speed_command =  self.speed_PID.step(speed_error, self.sample_time)
        throttle_command, brake_command = self.get_speed_control_vector(speed_command)

        # Comment out the steer pid, could be reactivated if needed
        steer = self.steer_PID.step(cte_value, self.sample_time)

        
        # To use the yaw_controller, activate the code below
        '''
        yaw_angle = self.LPF_angle.filt(yaw_angle) 
        steer = self.yaw_ctrl.get_steering(target_v, yaw_angle, actual_v)
        '''
        # Return throttle, brake, steer
        return throttle_command, brake_command, steer
