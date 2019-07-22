#!/usr/bin/python3

from ev3dev2.motor import OUTPUT_A, OUTPUT_B, SpeedPercent, MoveTank
from ev3dev2.sound import Sound
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("tag/networktest")

def on_message(client, userdata, msg):
    data = msg.payload.decode().split()
    comm = int(data[0])
    if comm == 0 and len(data) >= 2:
        sound = Sound()
        sound.speak(msg.payload.decode()[2:])
    elif comm == 1 and len(data) >= 4:
        print(int(data[1]),int(data[2]),int(data[3]))
        MoveTank(OUTPUT_B, OUTPUT_A).on_for_seconds(SpeedPercent(int(data[1])), SpeedPercent(int(data[2])), int(data[3]))
    #client.disconnect()


client = mqtt.Client()
client.username_pw_set("nyu", "nyu")
client.connect("192.168.1.127", 1883, 60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
