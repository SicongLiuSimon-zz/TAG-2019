#!/usr/bin/env python3
from ev3dev.ev3 import *

from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, SpeedPercent, MoveTank

import os
os.system('setfont Lat15-TerminusBold14')

print('Testing the Motors')
# Sound.speak('Hello, my name is EV3!').wait()

# Sound.play_song((('D4', 'e3'),('D4', 'e3'),('D4', 'e3'),('G4', 'h'),('D5', 'h')))

'''
mL = LargeMotor('outB')
mL.stop_action = 'hold'
mR = LargeMotor('outC')
mR.stop_action = 'hold'
'''

tank_drive = MoveTank('outB', 'outC')
tank_drive.on_for_rotations(SpeedPercent(25), SpeedPercent(25), 5)
tank_drive.on_for_rotations(SpeedPercent(25), SpeedPercent(25), -5)
tank_drive.on_for_rotations(SpeedPercent(25), SpeedPercent(25), 5)

'''
mL.on_for_rotations(SpeedPercent(75), 5)
mR.on_for_rotations(SpeedPercent(75), 5)
'''

# mL.run_to_rel_pos(position_sp= 840, speed_sp = 250)
# mR.run_to_rel_pos(position_sp=-840, speed_sp = 250)

'''
mL.wait_while('running')
mR.wait_while('running')
'''