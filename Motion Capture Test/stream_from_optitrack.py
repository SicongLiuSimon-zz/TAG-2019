from NatNetClient import NatNetClient
import paho.mqtt.client as mqtt
import struct

client = mqtt.Client()
client.username_pw_set("nyu", "nyu")
client.connect("192.168.1.102", 1883, 60)

def receiveRigidBodyFrame(id, pos, orient):
    # Update Values
    val = struct.pack('<4d',orient, pos[0], pos[1], pos[2])
    #client.publish("tag/optitrack_data", "{} {} {} {}".format(orient, pos[0], pos[1], pos[2]))
    #print(orient, pos[0], pos[1], pos[2])
    if id == 1:
        client.publish("tag/optitrack_data", val)

streamingClient = NatNetClient()

streamingClient.rigidBodyListener = receiveRigidBodyFrame

streamingClient.run()