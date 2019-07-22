from NatNetClient import NatNetClient
import paho.mqtt.client as mqtt
from datetime import datetime
from datetime import timedelta
import math

client = mqtt.Client()
client.username_pw_set("nyu", "nyu")
client.connect("192.168.1.127", 1883, 60)

time = datetime.now()
position = (0, 0, 0)
orientation = 0

buffer = True
tier = 1

# This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
def receiveRigidBodyFrame( pos, orient ):
    global time
    global position
    global orientation
    global buffer
    global tier

    # To not publish too many to mqtt
    if datetime.now() < time:
        return

    # Stop robot from moving and print initial data
    if buffer:
        print("Position      X:", pos[2], ", Y:", pos[0], ", Height:", pos[1])
        print("Orientation  ", orient)
        client.publish("tag/networktest", "MoveTank 0 0")
        buffer = not buffer

    # Update Values
    position = pos
    orientation = orient
    print("Position      X:", position[2], ", Y:", position[0], ", Height:", position[1])
    print("Orientation  ", orientation)
    print()

    '''
    # Go to (4, 2)
    if tier == 1:
        turn(orientation, 90)
    elif tier == 2:
        go_to_x(position, 4)
    elif tier == 3:
        turn(orientation, 0)
    elif tier == 4:
        go_to_y(position, 2)
    '''

    '''
    if tier == 1:
        turn(orientation, 90)
    elif tier == 2:
        go_to_x(position, 3)
    elif tier == 3:
        turn(orientation, 180)
    elif tier == 4:
        go_to_y(position, -3)
    elif tier == 5:
        turn(orientation, 270)
    elif tier == 6:
        go_to_x(position, 0)
    elif tier == 7:
        turn(orientation, 0)
    elif tier == 8:
        go_to_y(position, 0)
    elif tier == 9:
        turn(orientation, 90)
    elif tier == 10:
        go_to_x(position, 2)
    elif tier == 11:
        turn(orientation, 180)
    elif tier == 12:
        go_to_y(position, -2)
    elif tier == 13:
        turn(orientation, 270)
    elif tier == 14:
        go_to_x(position, 1)
    elif tier == 15:
        turn(orientation, 0)
    elif tier == 16:
        go_to_y(position, -1)
    '''

    '''
    # Danger Zone
    if danger_zone(position) < 2:
        print("DANGER!!!!!!!")
        client.publish("tag/networktest", "PlayFile danger.wav")
        time = datetime.now() + timedelta(seconds=3)

    # Put Me Down
    if position[1] > 4:
        print("PUT ME DOWN!!!!!!!")
        client.publish("tag/networktest", "PlayFile chime1.wav")
        time = datetime.now() + timedelta(seconds=3)
    '''

    '''
    # Say Location
    if position[1] > 5:
        print("I am at ", position)
        coordinate = position
        speech = "Speak I am at "
        if position[2] < 0:
            speech += "negative " + str(abs(position[2])) + " "
        else:
            speech += str(abs(position[2])) + " "
        if position[0] < 0:
            speech += "negative " + str(abs(position[0]))
        else:
            speech += str(abs(position[0]))
        client.publish("tag/networktest", speech)
        time = datetime.now() + timedelta(seconds=3)
    '''

def turn(orient, goal):
    global time
    global tier
    left_bound = goal - 7
    right_bound = goal + 7
    if left_bound < 0:
        left_bound = 360 + left_bound
        if (left_bound <= orient <= 360) or (0 <= orient <= right_bound):
            client.publish("tag/networktest", "MoveTank 0 0")
            tier += 1
        else:
            client.publish("tag/networktest", "MoveTank -10 10")
    elif right_bound > 360:
        right_bound = right_bound - 360
        if (left_bound <= orient <= 360) or (0 <= orient <= right_bound):
            client.publish("tag/networktest", "MoveTank 0 0")
            tier += 1
        else:
            client.publish("tag/networktest", "MoveTank -10 10")
    elif left_bound <= orient <= right_bound:
        client.publish("tag/networktest", "MoveTank 0 0")
        tier += 1
    elif left_bound - 20 <= orient <= right_bound + 20:
        client.publish("tag/networktest", "MoveTank -10 10")
    else:
        client.publish("tag/networktest", "MoveTank -50 50")
    time = datetime.now() + timedelta(seconds=0.5)

def go_to(pos, point):
    # Go to X first
    my_x = pos[0]
    my_y = pos[1]
    go_x = point[0]
    go_y = point[1]
    if my_x < go_x:
        turn(90)
    elif my_x > go_x:
        turn(270)

def go_to_x(pos, goal):
    global tier
    global time
    current = pos[2]
    if current == goal:
        client.publish("tag/networktest", "MoveTank 0 0")
        tier += 1
    elif goal - 1 <= current <= goal + 1:
        client.publish("tag/networktest", "MoveTank -10 -10")
    else:
        client.publish("tag/networktest", "MoveTank -50 -50")
    time = datetime.now() + timedelta(seconds=0.5)

def go_to_y(pos, goal):
    global tier
    global time
    current = pos[0]
    if current == goal:
        client.publish("tag/networktest", "MoveTank 0 0")
        tier += 1
    elif goal - 1 <= current <= goal + 1:
        client.publish("tag/networktest", "MoveTank -10 -10")
    else:
        client.publish("tag/networktest", "MoveTank -50 -50")
    time = datetime.now() + timedelta(seconds=0.5)

def danger_zone(position):
    current_x = position[2]
    current_y = position[0]
    origin_x = 0
    origin_y = 0

    x_diff = (abs(current_x - origin_x)) ** 2
    y_diff = (abs(current_y - origin_y)) ** 2
    radius = math.sqrt(x_diff + y_diff)

    return radius

# This will create a new NatNet client
streamingClient = NatNetClient()

# Configure the streaming client to call our rigid body handler on the emulator to send data out.
streamingClient.rigidBodyListener = receiveRigidBodyFrame

# Start up the streaming client now that the callbacks are set up.
# This will run perpetually, and operate on a separate thread.
streamingClient.run()