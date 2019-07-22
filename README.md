# Tag 2019

## Installation
```bash
pip install paho-mqtt
```
or 

follow [Install MQTT](https://www.ev3dev.org/docs/tutorials/sending-and-receiving-messages-with-mqtt/)
to set up MQTT

## Robot functions
subscribe.py receives commands from the MQTT server
```python
def on_connect(client, userdata, flags, rc):
    global logger
    print("Connected with result code " + str(rc))
    client.subscribe("tag/networktest")
```
connect to the server

Funcs_Table.py stores a dictionary of functions used in subscribe.py

danger.wav and chime1.wav are sound files

## Motion Capture
NatNetClient.py is OptiTrack's own script that receive data from the motion capture

```python
def quaternion_to_axis_angle(self, q):
    mul = 1.0 / math.sqrt(1 - q[3] * q[3])
    return [q[0] * mul, q[1] * mul, q[2] * mul, math.acos(q[3]) * 2.0]

def axis_angle_to_matrix(self, aa):
    c = math.cos(aa[3])
    s = math.sin(aa[3])
    t = 1 - c
    return [[t * aa[0] * aa[0] + c, t * aa[0] * aa[1] - aa[2] * s, t * aa[0] * aa[2] + aa[1] * s],
            [t * aa[0] * aa[1] + aa[2] * s, t * aa[1] * aa[1] + c, t * aa[1] * aa[2] - aa[0] * s],
            [t * aa[0] * aa[2] - aa[1] * s, t * aa[1] * aa[2] + aa[0] * s, t * aa[2] * aa[2] + c]]

def quarternion_to_matrix(self, q):
    return self.axis_angle_to_matrix(self.quaternion_to_axis_angle(q))

def lazy_angle(self, q):
    mat = self.quarternion_to_matrix(q)
    x_vec = [mat[0][0], mat[1][0], mat[2][0]]
    if mat[1][1] < 0:
        x_vec[0] *= -1
        x_vec[1] *= -1
        x_vec[2] *= -1
    return math.atan2(x_vec[0], x_vec[2])
```
These functions aim to transform quaternion to angle to get orientation of the robot

tag_project.py is the main script controlling the robot to do tasks
Tasks include accurate turning, forwarding and moving to certain coordinate


```python
def commands(self):
    self.client.publish("tag/networktest", "MoveTank 0 0")
    time.sleep(1)
    while True:
        # self.turn(0)
        # self.move_to( (1, 1) )
        # self.straight_to((-4, -4))
        # self.moveTo((1,1), 0.5)
        break
```
This function sends commands to the robot to do different tasks

## Poster
<img src="TAG Poster.png" width=1000><br>

