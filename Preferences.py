from comm.Serial import DataType_Int, DataType_Float, DataType_Boolean

preferences = {
	"FF:FF:FF:FF:FF:FF" : [
        # PID Controllers
		{"data_type": DataType_Boolean, "key": "zEn", "value": True}, # Enable height controller
		{"data_type": DataType_Boolean, "key": "rollEn", "value": False}, # Enable roll controller
		{"data_type": DataType_Boolean, "key": "rotateEn", "value": False}, # Enable rotation controller
		{"data_type": DataType_Boolean, "key": "pitchEn", "value": False}, # Enable pitch controller
		{"data_type": DataType_Boolean, "key": "yawEn", "value": True}, # Enable yaw controller

		{"data_type": DataType_Float, "key": "kpyaw", "value": 1.7}, # Proportional value for yaw controller
		{"data_type": DataType_Float, "key": "kppyaw", "value": 0.03}, 
		{"data_type": DataType_Float, "key": "kdyaw", "value": 0.045}, # Derivative value for yaw controller
		{"data_type": DataType_Float, "key": "kddyaw", "value": 0.03},
		{"data_type": DataType_Float, "key": "kiyaw", "value": 0}, # Integral value for yaw controller
		{"data_type": DataType_Float, "key": "kiyawrate", "value": 0},

		{"data_type": DataType_Float, "key": "kpz", "value": 2.5}, # Proportional value for height controller
		{"data_type": DataType_Float, "key": "kdz", "value": 1.2}, # Derivative value for height controller
		{"data_type": DataType_Float, "key": "kiz", "value": 0.0}, # Integral value for yaw controller

		{"data_type": DataType_Float, "key": "kproll", "value": 0}, # Proportional value for roll controller
		{"data_type": DataType_Float, "key": "kdroll", "value": 0}, # Derivative value for roll controller
		{"data_type": DataType_Float, "key": "kppitch", "value": 0}, # Proportional value for pitch controller
		{"data_type": DataType_Float, "key": "kdpitch", "value": -0.3}, # Derivative value pitch controller

		{"data_type": DataType_Float, "key": "z_int_low", "value": 0}, 
		{"data_type": DataType_Float, "key": "z_int_high", "value": 0.15},
		{"data_type": DataType_Float, "key": "yawRateIntRange", "value": 0},
		{"data_type": DataType_Float, "key": "lx", "value": 0.1},
        
		# A-matrix adjustments for the servo
		{"data_type": DataType_Float, "key": "servoRange", "value": 360}, # Range of values for the servo
		{"data_type": DataType_Float, "key": "servoBeta", "value": 180}, # Initial point of the value
		{"data_type": DataType_Float, "key": "servo_move_min", "value": 0},
		{"data_type": DataType_Float, "key": "botZlim", "value": -1},
		{"data_type": DataType_Float, "key": "pitchOffset", "value": 0},
		{"data_type": DataType_Float, "key": "pitchInvert", "value": -1},
		
		{"data_type": DataType_Int, "key": "num_charges", "value": 4}, # Number of charges before switching to the next mode
		{"data_type": DataType_Int, "key": "time_in_mode", "value": 120}, # Time(s) that a robot will continue searching before switching to another mode
		{"data_type": DataType_Int, "key": "charge_time", "value": 15}, # Number of seconds that a robot will charge
        {"data_type": DataType_Int, "key": "target_color", "value": 0x80}, # Target color for the goal, 0x80 = yellow, 0x81 = orange
		{"data_type": DataType_Float, "key": "default_height", "value": 9}, # Default height for the goal mode
		{"data_type": DataType_Float, "key": "height_range", "value": 3}, # Height bounds Ex. default_height = 9, height_range = 2, 7 < height < 11
		{"data_type": DataType_Float, "key": "wall_thresh", "value": 250}, # Threshold before wall avoidance is triggered

		{"data_type": DataType_Float, "key": "y_thresh", "value": 0.55}, # Camera will try to align the center of target to this threshold, higher means robot will try to be below target
		{"data_type": DataType_Float, "key": "y_strength", "value": 2.0}, # How sensitive the robot will be to height difference of the target
		{"data_type": DataType_Float, "key": "x_strength", "value": 1}, # How sensitive the robot will be to the yaw difference of the target
		{"data_type": DataType_Float, "key": "fx_togoal", "value": 0.3}, # Speed at which robot approaches the goal
		{"data_type": DataType_Float, "key": "fx_charge", "value": 0.6}, # Speed at which robot charges at the goal
        

		{"data_type": DataType_Float, "key": "fx_levy", "value": 0.3}, # Speed at which the robot will search
		{"data_type": DataType_Float, "key": "fz_levy", "value": 0.5}, # Range of height that the robot can randomly choose during levy spiral        

		{"data_type": DataType_Int, "key": "n_max_x", "value": 240}, # Max number of pixels in the x-direction for the camera
		{"data_type": DataType_Int, "key": "n_max_y", "value": 160}, # Max number of pixels in the y-direction for the camera
		{"data_type": DataType_Float, "key": "h_ratio", "value": 0.85}, # Value that determines the threshold before charging
		{"data_type": DataType_Float, "key": "range_for_forward", "value": 0.16}, # Determines how centered the target must be before approaching target
		
		{"data_type": DataType_Int, "key": "bnum_charges", "value": 3},
		{"data_type": DataType_Int, "key": "btime_in_mode", "value": 120},
		{"data_type": DataType_Int, "key": "bcharge_time", "value": 6},
        {"data_type": DataType_Int, "key": "btarget_color", "value": 0x40},
		{"data_type": DataType_Float, "key": "bdefault_height", "value": 2},
		{"data_type": DataType_Float, "key": "bheight_range", "value": 3},
		{"data_type": DataType_Float, "key": "bwall_thresh", "value": 250},
		
		{"data_type": DataType_Float, "key": "by_thresh", "value": 0.49},
		{"data_type": DataType_Float, "key": "by_strength", "value": 1.4},
		{"data_type": DataType_Float, "key": "bx_strength", "value": 1.3},
		{"data_type": DataType_Float, "key": "bfx_togoal", "value": 0.21},
		{"data_type": DataType_Float, "key": "bfx_charge", "value": 0.5},
        

		{"data_type": DataType_Float, "key": "bfx_levy", "value": 0.4},
		{"data_type": DataType_Float, "key": "bfz_levy", "value": 1.5},

		{"data_type": DataType_Int, "key": "bn_max_x", "value": 240},
		{"data_type": DataType_Int, "key": "bn_max_y", "value": 160},
		{"data_type": DataType_Float, "key": "bh_ratio", "value": 0.4},
		{"data_type": DataType_Float, "key": "brange_for_forward", "value": 0.08}
    ],
    
    "attacker" : [		
		{"data_type": DataType_Int, "key": "bnum_charges", "value": 100},
		{"data_type": DataType_Int, "key": "btime_in_mode", "value": 300},
		{"data_type": DataType_Int, "key": "bcharge_time", "value": 8},
        {"data_type": DataType_Int, "key": "btarget_color", "value": 0x41},
		{"data_type": DataType_Float, "key": "bdefault_height", "value": 4},
		{"data_type": DataType_Float, "key": "bheight_range", "value": 3},
		{"data_type": DataType_Float, "key": "bwall_thresh", "value": 250},
		
		{"data_type": DataType_Float, "key": "by_thresh", "value": 0.5},
		{"data_type": DataType_Float, "key": "by_strength", "value": 1.3},
		{"data_type": DataType_Float, "key": "bx_strength", "value": 2.5},
		{"data_type": DataType_Float, "key": "bfx_togoal", "value": 0.8},
		{"data_type": DataType_Float, "key": "bfx_charge", "value": 0.8},
        

		{"data_type": DataType_Float, "key": "bfx_levy", "value": 0.3},
		{"data_type": DataType_Float, "key": "bfz_levy", "value": 2.5},
		{"data_type": DataType_Float, "key": "blevy_yaw", "value": 0.02},
        {"data_type": DataType_Float, "key": "bpercent_spiral", "value": 0.0},

		{"data_type": DataType_Float, "key": "bh_ratio", "value": 4},
		{"data_type": DataType_Float, "key": "brange_for_forward", "value": 0.25}
	],
    
    "defender" : [
        {"data_type": DataType_Int, "key": "num_charges", "value": 400},
        {"data_type": DataType_Int, "key": "time_in_mode", "value": 3000},
        {"data_type": DataType_Int, "key": "charge_time", "value": 3},
        {"data_type": DataType_Int, "key": "target_color", "value": 0x81},
        {"data_type": DataType_Float, "key": "default_height", "value": 8},
        {"data_type": DataType_Float, "key": "height_range", "value": 2},
        {"data_type": DataType_Float, "key": "wall_thresh", "value": 250},
        {"data_type": DataType_Float, "key": "y_thresh", "value": 0.5},
        {"data_type": DataType_Float, "key": "y_strength", "value": 1.5},
        {"data_type": DataType_Float, "key": "x_strength", "value": 1.4},
        {"data_type": DataType_Float, "key": "fx_togoal", "value": 0.6},
        {"data_type": DataType_Float, "key": "fx_charge", "value": 0.8},
        {"data_type": DataType_Float, "key": "fx_levy", "value": 0.8},
        {"data_type": DataType_Float, "key": "fz_levy", "value": 0.5},
        {"data_type": DataType_Int, "key": "n_max_x", "value": 240},
        {"data_type": DataType_Int, "key": "n_max_y", "value": 160},
        {"data_type": DataType_Float, "key": "h_ratio", "value": 0.8},
        {"data_type": DataType_Float, "key": "range_for_forward", "value": 0.16},
        {"data_type": DataType_Float, "key": "percent_spiral", "value": 0.5},
    ],
    
	"orange" : [
        {"data_type": DataType_Int, "key": "num_charges", "value": 1},
		{"data_type": DataType_Int, "key": "time_in_mode", "value": 300},
		{"data_type": DataType_Int, "key": "charge_time", "value": 10},
        {"data_type": DataType_Int, "key": "target_color", "value": 0x80},
		{"data_type": DataType_Float, "key": "default_height", "value": 9},
		{"data_type": DataType_Float, "key": "height_range", "value": 2},
		{"data_type": DataType_Float, "key": "wall_thresh", "value": 250},

		{"data_type": DataType_Float, "key": "y_thresh", "value": 0.65},
		{"data_type": DataType_Float, "key": "y_strength", "value": 0.7},
		{"data_type": DataType_Float, "key": "x_strength", "value": 2},
		{"data_type": DataType_Float, "key": "fx_togoal", "value": 0.3},
		{"data_type": DataType_Float, "key": "fx_charge", "value": 0.6},
        

		{"data_type": DataType_Float, "key": "fx_levy", "value": 0.2},
		{"data_type": DataType_Float, "key": "fz_levy", "value": 0.5},      

		{"data_type": DataType_Int, "key": "n_max_x", "value": 160},#160 ==> 240
		{"data_type": DataType_Int, "key": "n_max_y", "value": 120},#120 ==> 160
		{"data_type": DataType_Float, "key": "h_ratio", "value": 0.8},
		{"data_type": DataType_Float, "key": "range_for_forward", "value": 0.16},
        {"data_type": DataType_Int, "key": "target_color", "value": 0x81},
	],
    
	"yellow" : 
    [
        {"data_type": DataType_Int, "key": "num_charges", "value": 1},
		{"data_type": DataType_Int, "key": "time_in_mode", "value": 300},
		{"data_type": DataType_Int, "key": "charge_time", "value": 10},
        {"data_type": DataType_Int, "key": "target_color", "value": 0x80},
		{"data_type": DataType_Float, "key": "default_height", "value": 9},
		{"data_type": DataType_Float, "key": "height_range", "value": 2},
		{"data_type": DataType_Float, "key": "wall_thresh", "value": 250},

		{"data_type": DataType_Float, "key": "y_thresh", "value": 0.65},
		{"data_type": DataType_Float, "key": "y_strength", "value": 0.7},
		{"data_type": DataType_Float, "key": "x_strength", "value": 2},
		{"data_type": DataType_Float, "key": "fx_togoal", "value": 0.3},
		{"data_type": DataType_Float, "key": "fx_charge", "value": 0.6},
        

		{"data_type": DataType_Float, "key": "fx_levy", "value": 0.2},
		{"data_type": DataType_Float, "key": "fz_levy", "value": 0.5},      

		{"data_type": DataType_Int, "key": "n_max_x", "value": 240},
		{"data_type": DataType_Int, "key": "n_max_y", "value": 160},
		{"data_type": DataType_Float, "key": "h_ratio", "value": 0.8},
		{"data_type": DataType_Float, "key": "range_for_forward", "value": 0.16},
        {"data_type": DataType_Int, "key": "target_color", "value": 0x80},
	],
    
	}

PREFERENCES = {k.lower(): v for k, v in preferences.items()}