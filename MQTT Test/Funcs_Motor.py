"""
Wrapper for the Motor functionality of ev3
Default motor pair set to A, B. Update using SetTankFunc
"""
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, SpeedPercent, MoveTank

tank = MoveTank(OUTPUT_A, OUTPUT_B)
MotorTable = dict()
MotorTable['A'] = OUTPUT_A
MotorTable['B'] = OUTPUT_B
MotorTable['C'] = OUTPUT_C

def SetTankFunc(param):
    data=param.split()
    global tank
    tank = MoveTank(MotorTable[data[0]], MotorTable[data[1]])

def MoveTankFunc(param):
    if tank is None:
        return
    data=param.split()
    tank.on(SpeedPercent(int(data[0])), SpeedPercent(int(data[1])))

def MoveTankDegreesFunc(param):
    if tank is None:
        return
    data=param.split()
    tank.on_for_degrees(SpeedPercent(int(data[0])), SpeedPercent(int(data[1])), float(data[2]))

def MoveTankRotationFunc(param):
    if tank is None:
        return
    data=param.split()
    tank.on_for_rotations(SpeedPercent(int(data[0])), SpeedPercent(int(data[1])), float(data[2]))

def MoveTankDurationFunc(param):
    if tank is None:
        return
    data=param.split()
    tank.on_for_seconds(SpeedPercent(int(data[0])), SpeedPercent(int(data[1])), float(data[2]))

def init(FunctionTable):
    FunctionTable["SetTank"] = SetTankFunc
    FunctionTable["MoveTank"] = MoveTankFunc
    FunctionTable["MoveTankDegrees"] = MoveTankDegreesFunc
    FunctionTable["MoveTankRotation"] = MoveTankRotationFunc
    FunctionTable["MoveTankDuration"] = MoveTankDurationFunc