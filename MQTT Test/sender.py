#!/usr/bin/python3
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.username_pw_set("nyu", "nyu")
client.connect("192.168.1.127", 1883, 60)

client.publish("tag/networktest", "SetTank A B")
while True:
    client.publish("tag/networktest", "Hi")

"""
while True:
    try:
        send = ""
        print ("enter command num")
        send += str(int(input()))
        if send=="0":
            print("enter words")
            send += " " + input()
        elif send=="1":
            print("enter values left, right, duration")
            send += " " + str(int(input()))
            send += " " + str(int(input()))
            send += " " + str(int(input()))
        print(send)
        client.publish("tag/networktest", send)
    except:
        print("put in proper values")
"""
client.disconnect()