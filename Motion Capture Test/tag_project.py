from NatNetClient import NatNetClient
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
import time
import math
from threading import Thread
import queue

class Tag:
    def __init__(self):
        self.time = datetime.now()
        self.position = (0, 0, 0)
        self.orientation = 0
        self.ideal_orientation = 0 # to keep track of desired orientation, not measured
        self.function_table = {}

        self.function_table["Move"] = self._move
        self.function_table["Rotate"] = self._turn
        self.function_table["Draw"] = self._draw
        self.function_table["Position"] = self._getposition

        self.queue = queue.Queue()

        self.fast_movement = "MoveTank 70 70"
        self.fast_reverse_movement = "MoveTank -70 -70"
        self.slow_movement = "MoveTank 30 30"
        self.slow_reverse_movement = "MoveTank -30 -30"

        self.stop_movement = "MoveTank 0 0"

        self.slow_right_turn = "MoveTank 10 -10"
        self.slow_left_turn = "MoveTank -10 10"
        self.fast_right_turn = "MoveTank 20 -20"
        self.fast_left_turn = "MoveTank -20 20"

        self.streamingClient = NatNetClient()
        self.streamingClient.rigidBodyListener = self.receiveRigidBodyFrame
        self.streamingClient.run()

        self.client = mqtt.Client()
        self.client.username_pw_set("nyu", "nyu")
        self.client.connect("192.168.1.102", 1883, 60)

        # Next Steps: CoreLink
        # To Do: Go to position using iPad and Speech to Text, Draw Shapes, Queue

    def __del__(self):
        self.client.disconnect()

    # MQTT subcribing and connecting to iPad
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe("tag/iosaction")
        print("Subscribed")
    def on_message(self, client, userdata, msg):
        data = msg.payload.decode()
        print(data)
        split = data.find(' ')
        action = data[:split]
        param = data[split + 1:]
        if action != "Position":
            self.queue.enqueue(self.function_table[action](param))
        else:
            self.function_table[action](param)
    def receiveRigidBodyFrame(self, pos, orient):
        # Update Values
        self.position = pos
        self.orientation = orient

        # To not publish too many to mqtt
        if datetime.now() < self.time:
            return

        if self.position[1] > 5:
            print("PUT ME DOWN!!!!!!!")
            self.client.publish("tag/iostest", "Say Put Me Down")
            self.time = datetime.now() + timedelta(seconds=3)
        else:
            print("Position      X:", self.position[2], ", Y:", self.position[0], ", Height:", self.position[1])
            print("Orientation  ", self.orientation)
            print()
            self.time = datetime.now() + timedelta(seconds=2)

    # IOS Integration for Function Table Subscribing
    def _getposition(self, val):
        print("I am at ", self.position)
        speech = "I am at "
        if round(self.position[2]) < 0:
            speech += "negative " + str(round(abs(self.position[2]))) + " "
        else:
            speech += str(round(abs(self.position[2]))) + " "
        if round(self.position[0]) < 0:
            speech += "negative " + str(round(abs(self.position[0])))
        else:
            speech += str(round(abs(self.position[0])))
        self.client.publish("tag/iosspeak", speech)
    def _draw(self, val):
        self.client.publish("tag/iosspeak", "HEEEEEIIII")
        if val == "Square":
            print("SQUARE")
            self.draw_square(1)
        elif val == "Triangle":
            print("Triangle")
            self.draw_equil_triangle(1)
        elif val == "Circle":
            print("Circle")
            self.draw_circle(1)
        self.queue.dequeue()
    def _turn(self, val):
        self.client.publish("tag/iosspeak", "HEEEEEEA")
        if val == "Left":
            if self.ideal_orientation + 90 > 360:
                self.turn(90)
            else:
                self.turn(self.ideal_orientation + 90)
        else:
            if self.ideal_orientation - 90 < 0:
                self.turn(270)
            else:
                self.turn(self.ideal_orientation - 90)
        self.queue.dequeue()
    def _move(self, val):
        self.client.publish("tag/iosspeak", "HELLO")
        if val == "Up":
            self.move(1)
        elif val == "Down":
            self.move(-1)
        self.queue.dequeue()

    # Turning and Moving Methods
    def turn(self, goal):
        print("Turning to", goal, "degrees")
        self.ideal_orientation = goal
        # Find out whether to turn left or right based on closest
        diff = abs(goal - self.orientation)

        right = False # False if 0 degrees is right
        if diff < 180:
            if goal < self.orientation:
                right = not right
        elif diff > 180:
            if goal > self.orientation:
                right = not right

        left_bound = goal - 2
        right_bound = goal + 2
        if goal - 2 < 0:
            left_bound = 360 + left_bound
        elif goal + 2 > 360:
            right_bound = right_bound - 360

        if right:
            self.client.publish("tag/networktest", self.slow_right_turn)
        else:
            self.client.publish("tag/networktest", self.slow_left_turn)

        while True:
            if goal - 2 < 0 or goal + 2 > 360:
                if (left_bound <= self.orientation <= 360) or (0 <= self.orientation <= right_bound):
                    self.client.publish("tag/networktest", self.stop_movement)
                    break
            elif left_bound <= self.orientation <= right_bound:
                self.client.publish("tag/networktest", self.stop_movement)
                break
    def move(self, length):
        print("Moving", length, "feet")
        change_x = length * math.cos(self.orientation / 180 * math.pi)

        change_y = length * math.sin(self.orientation / 180 * math.pi)

        goal = (self.position[2] + change_x, self.position[0] + change_y)

        left_bound_x = goal[0] - 0.07
        right_bound_x = goal[0] + 0.07
        left_bound_y = goal[1] - 0.07
        right_bound_y = goal[1] + 0.07

        if length > 0:
            self.client.publish("tag/networktest", self.slow_movement)
            self.client.publish("tag/iosspeak", "HELLO")
        else:
            self.client.publish("tag/networktest", self.slow_reverse_movement)
            self.client.publish("tag/iosspeak", "HELLO")

        while True:
            if left_bound_x <= self.position[2] <= right_bound_x and left_bound_y <= self.position[0] <= right_bound_y:
                self.client.publish("tag/networktest", self.stop_movement)
                break

    # Turning and Moving Helper Methods: Fixed on_connect and while loop problem by implementing threads
    # Current Fix: Receiving commands on same thread, but carrying out on separate thread
    # Could try having a queue that completes actions on a separate thread, but no need for separate thread for turning/moving
    def turning_loop(self, goal, left_bound, right_bound):
        while True:
            if goal - 2 < 0 or goal + 2 > 360:
                if (left_bound <= self.orientation <= 360) or (0 <= self.orientation <= right_bound):
                    self.client.publish("tag/networktest", self.stop_movement)
                    break
            elif left_bound <= self.orientation <= right_bound:
                self.client.publish("tag/networktest", self.stop_movement)
                break
    def moving_loop(self, left_bound_x, right_bound_x, left_bound_y, right_bound_y):
        while True:
            if left_bound_x <= self.position[2] <= right_bound_x and left_bound_y <= self.position[0] <= right_bound_y:
                self.client.publish("tag/networktest", self.stop_movement)
                break

    # Draw Shapes Methods
    def draw_square(self, length):
        area = length ** 2
        # Increase Change in Y
        self.move_to_y(self.position[0] + length)
        # Increase Change in X
        self.move_to_x(self.position[2] + length)
        # Decrease Change in Y
        self.move_to_y(self.position[0] - length)
        # Decrease Change in X
        self.move_to_x(self.position[2] - length)
        # Say Area
        self.client.publish("tag/iosspeak", "The area of the square is {}".format(area))
    def draw_equil_triangle(self, length):
        area = (1/2) * length * length
        # 60 Degree Turn
        self.turn(60)
        self.move(length)
        self.turn(300)
        self.move(length)
        self.turn(180)
        self.move(length)
        # Say Area
        self.client.publish("tag/iosspeak", "Speak The area of the triangle is {}".format(area))
    def draw_circle(self, radius):
        pass

    # Coordinate Grid Methods: Moving To Point using X/Y or Straight There
    def moveTo(self, goal, error):
        var = (goal[0] - self.position[2], goal[1] - self.position[0])
        mag = math.sqrt((var[0])**2 + (var[1])**2)
        angle = math.atan2(var[1], var[0]) * 180 / math.pi
        diff = angle - self.orientation

        a = abs((math.atan((goal[1] - self.position[0]) / (goal[0] - self.position[2])) * 180 / math.pi))
        if goal[0] > self.position[2]:  # right
            if goal[1] > self.position[0]:  # up
                angle = 90 - a
            else:  # down
                angle = 90 + a
        else:  # left
            if goal[1] > self.position[0]:  # up
                angle = 270 + a
            else:  # down
                angle = 270 - a

        print(angle)

        self.turn(angle)

        # self.client.publish("tag/networktest", self.slow_movement)

        print("HIIIIIIIIIIIII")

        while True:
            left_bound_x = goal[0] - 0.05
            right_bound_x = goal[0] + 0.05
            left_bound_y = goal[1] - 0.05
            right_bound_y = goal[1] + 0.05

            if left_bound_x <= self.position[2] <= right_bound_x and left_bound_y <= self.position[0] <= right_bound_y:
                self.client.publish("tag/networktest", "MoveTank 0 0")
                break

            if mag < error:
                print(1)
                self.turn(angle)
                # self.client.publish("tag/networktest", self.slow_movement)
                continue

            if abs(diff) >= 90:
                print(2)
                self.turn(angle)
                # self.client.publish("tag/networktest", self.slow_movement)
                continue

            if mag * math.sin(abs(diff)) > error:
                print(3)
                self.turn(angle)
                # self.client.publish("tag/networktest", self.slow_movement)
                continue
            else:
                print(4)
                continue
    def straight_to(self, goal):
        # robot moves straight to coordinate point
        a = abs((math.atan((goal[1] - self.position[0]) / (goal[0] - self.position[2])) * 180 / math.pi))

        if goal[0] > self.position[2]:  # right
            if goal[1] > self.position[0]:  # up
                angle = a
            else: # down
                angle = 360 + a
        else: # left
            if goal[1] > self.position[0]:  # up
                angle = 180 + a
            else: # down
                angle = 180 + a

        self.turn(angle)
        self.client.publish("tag/networktest", self.slow_movement)
        left_bound_x = goal[0] - 0.07
        right_bound_x = goal[0] + 0.07
        left_bound_y = goal[1] - 0.07
        right_bound_y = goal[1] + 0.07

        while True:
            # print("Going Straight to {}".format(goal), (self.position[2], self.position[0]))
            if left_bound_x <= self.position[2] <= right_bound_x and left_bound_y <= self.position[0] <= right_bound_y:
                self.client.publish("tag/networktest", self.stop_movement)
                break
            # elif left_bound_x <= self.position[2] <= right_bound_x:
            #     self.client.publish("tag/networktest", "MoveTank 0 0")
            #     # self.straight_to(goal)
            #     break
            # elif left_bound_y <= self.position[0] <= right_bound_y:
            #     self.client.publish("tag/networktest", "MoveTank 0 0")
            #     # self.straight_to(goal)
            #     break
        self.turn(90)
    def move_to(self, goal):
        # robot moves to coordinate point using x and y
        self.move_to_x(goal[0])
        self.move_to_y(goal[1])
    def move_to_x(self, goal):
        left_bound = goal - 0.03
        right_bound = goal + 0.03
        if goal - self.position[2] > 0:
            self.turn(0)
        elif goal - self.position[2] < 0:
            self.turn(180)
        self.client.publish("tag/networktest", self.fast_movement)
        while True:
            # print("Going to X = {}".format(goal))
            if left_bound <= self.position[2] <= right_bound:
                self.client.publish("tag/networktest", self.stop_movement)
                break
    def move_to_y(self, goal):
        left_bound = goal - 0.03
        right_bound = goal + 0.03
        if goal - self.position[0] > 0:
            self.turn(90)
        elif goal - self.position[0] < 0:
            self.turn(270)
        self.client.publish("tag/networktest", self.fast_movement)
        while True:
            # print("Turning to Y = {}".format(goal))
            if left_bound <= self.position[0] <= right_bound:
                self.client.publish("tag/networktest", self.stop_movement)
                break
        self.turn(90)

    # MQTT separate thread because loop forever has issues after calling that method
    def mqtt_setup(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_forever()

    # Main method for testing
    def commands(self):
        self.client.publish("tag/networktest", self.stop_movement)
        time.sleep(0.5)
        # self.move(1)
        # self.turn(330)

        # self.straight_to((-1, -3))
        # self.move_to_x(-3)
        # self.move_to_y(-3)
        # self.moveTo((1,-1), 0.5)

        # self.move_to((2, -2))
        # self.turn(90)

        # self.move(2)

        # self.turn(60)
        # self.move(1)
        # self.turn(300)
        # self.move(1)
        # self.turn(180)

        # self.draw_equil_triangle(2)
        # self.draw_square(3)
        while True:
            print(self.queue.get())

    def run(self):
        m = Thread(target = self.mqtt_setup)
        t = Thread(target = self.commands)
        m.start()
        t.start()

# Current Fix with turning_loop/moving_loop helpers
'''
Robot receives commands from iOS app on separate thread
Robot runs commands method from mac on separate thread
Robot performs actions (turning, moving) on separate thread
Mac receives data from Optrack on separate thread
'''

# Work in Progress
'''
Threads: on_connect, OptiTrack, commands(does movement queues: turn, move,straight_to)
Add each command to queue, then dequeue after it is finished; these commands are carried out in commands thread
'''

robot = Tag()
robot.run()