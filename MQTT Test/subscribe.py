#!/usr/bin/python3
import paho.mqtt.client as mqtt
from Funcs_Table import FunctionTable
import datetime

def on_connect(client, userdata, flags, rc):
    global logger
    print("Connected with result code " + str(rc))
    client.subscribe("tag/networktest")

def on_message(client, userdata, msg):
    data = msg.payload.decode()
    split = data.find(' ')
    FunctionTable[data[:split]](data[split+1:])
    with open("log.txt", 'a') as file:
        file.write(str(datetime.datetime.now()) + " " + str(data) + "\n")

client = mqtt.Client()
client.username_pw_set("nyu", "nyu")
#ip address of mqtt broker
client.connect("192.168.1.102", 1883, 60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
