from ev3dev2.sound import Sound
speaker = Sound()
import os

def SpeakFunc(param):
    speaker.speak(param)

def PlayFileFunc(param):
    # speaker.play_file(param)
    os.system("aplay " + param)
    print("Playing")


def init(FunctionTable):
    FunctionTable["Speak"] = SpeakFunc
    FunctionTable["PlayFile"] = PlayFileFunc

