﻿import socket
import struct
from threading import Thread
import time
import math


def trace(*args):
    pass  # print( "".join(map(str,args)) )


# Create structs for reading various object types to speed up parsing.
Vector3 = struct.Struct('<fff')
Quaternion = struct.Struct('<ffff')
FloatValue = struct.Struct('<f')
DoubleValue = struct.Struct('<d')


class NatNetClient:
    def __init__(self):
        # Change this value to the IP address of the NatNet server.
        self.serverIPAddress = "169.254.201.120"

        # This should match the multicast address listed in Motive's streaming settings.
        self.multicastAddress = "239.255.42.99"

        # NatNet Command channel
        self.commandPort = 1510

        # NatNet Data channel
        self.dataPort = 1511

        # Set this to a callback method of your choice to receive per-rigid-body data at each frame.
        self.rigidBodyListener = None

        # NatNet stream version. This will be updated to the actual version the server is using during initialization.
        self.__natNetStreamVersion = (2, 10, 0, 0)  # (3,0,0,0)

    # Client/server message ids
    NAT_PING = 0
    NAT_PINGRESPONSE = 1
    NAT_REQUEST = 2
    NAT_RESPONSE = 3
    NAT_REQUEST_MODELDEF = 4
    NAT_MODELDEF = 5
    NAT_REQUEST_FRAMEOFDATA = 6
    NAT_FRAMEOFDATA = 7
    NAT_MESSAGESTRING = 8
    NAT_DISCONNECT = 9
    NAT_UNRECOGNIZED_REQUEST = 100

    # Create a data socket to attach to the NatNet stream
    def __createDataSocket(self, port):
        result = socket.socket(socket.AF_INET,  # Internet
                               socket.SOCK_DGRAM,
                               socket.IPPROTO_UDP)  # UDP
        result.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        result.bind(('', port))

        mreq = struct.pack("4sl", socket.inet_aton(self.multicastAddress), socket.INADDR_ANY)
        result.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        return result

    # Create a command socket to attach to the NatNet stream
    def __createCommandSocket(self):
        result = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        result.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        result.bind(('', 0))
        result.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        return result


























    # Quaternion Conversion Functions
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

        return math.atan2(x_vec[0], x_vec[2]) # if 0 is right, positive x-axis
        # return math.atan2(x_vec[2], x_vec[0])

    # Unpack a rigid body object from a data packet
    def __unpackRigidBody(self, data):
        offset = 0

        # ID (4 bytes)
        id = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("ID:", id)

        # Position (Motive: forward  X, up Y, left Z) (In Person: Y, X, Height)
        # pos is in meter; m to feet (multiply by 3.281)
        pos = Vector3.unpack(data[offset:offset + 12])
        position = (pos[0] * 3.281, pos[1] * 3.281, pos[2] * 3.281)
        '''
        if pos[0] < 0:
            pos[0] = math.ceil(pos[0])
        else:
            pos[0] = math.floor(pos[0])
        if pos[1] < 0:
            pos[1] = math.ceil(pos[1])
        else:
            pos[1] = math.floor(pos[1])
        if pos[2] < 0:
            pos[2] = math.ceil(pos[2])
        else:
            pos[2] = math.floor(pos[2])
        position = (pos[0] , pos[1] , pos[2] )
        '''
        offset += 12
        trace("\tPosition:", pos[0], ",", pos[1], ",", pos[2])

        # Orientation (x, y, z, w)
        # 0 to 90, 90 to 180, -180 to -90, -90 to 0
        rot = Quaternion.unpack(data[offset:offset + 16])
        offset += 16
        trace("\tOrientatianlgon:", rot[0], ",", rot[1], ",", rot[2], ",", rot[3])
        orientation = self.lazy_angle(rot) * 180 / math.pi
        if orientation < 0:
            orientation += 360

        # Marker count (4 bytes)
        markerCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        markerCountRange = range(0, markerCount)
        trace("\tMarker Count:", markerCount)

        # Send information to any listener.
        if self.rigidBodyListener is not None:
            self.rigidBodyListener(position, orientation)

        # Marker positions
        for i in markerCountRange:
            pos = Vector3.unpack(data[offset:offset + 12])
            offset += 12
            trace("\tMarker", i, ":", pos[0], ",", pos[1], ",", pos[2])

        if (self.__natNetStreamVersion[0] >= 2):
            # Marker ID's
            for i in markerCountRange:
                id = int.from_bytes(data[offset:offset + 4], byteorder='little')
                offset += 4
                trace("\tMarker ID", i, ":", id)

            # Marker sizes
            for i in markerCountRange:
                size = FloatValue.unpack(data[offset:offset + 4])
                offset += 4
                trace("\tMarker Size", i, ":", size[0])

            markerError, = FloatValue.unpack(data[offset:offset + 4])
            offset += 4
            trace("\tMarker Error:", markerError)

        # Version 2.6 and later
        if (((self.__natNetStreamVersion[0] == 2) and (self.__natNetStreamVersion[1] >= 6)) or
                self.__natNetStreamVersion[0] > 2 or self.__natNetStreamVersion[0] == 0):
            param, = struct.unpack('h', data[offset:offset + 2])
            trackingValid = (param & 0x01) != 0
            offset += 2
            trace("\tTracking Valid:", 'True' if trackingValid else 'False')

        return offset











































    # Unpack a skeleton object from a data packet
    def __unpackSkeleton(self, data):
        offset = 0

        id = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("ID:", id)

        rigidBodyCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("Rigid Body Count:", rigidBodyCount)
        for j in range(0, rigidBodyCount):
            offset += self.__unpackRigidBody(data[offset:])

        return offset

    # Unpack data from a motion capture frame message
    def __unpackMocapData(self, data):
        trace("Begin MoCap Frame\n-----------------\n")

        data = memoryview(data)
        offset = 0

        # Frame number (4 bytes)
        frameNumber = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("Frame #:", frameNumber)

        # Marker set count (4 bytes)
        markerSetCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("Marker Set Count:", markerSetCount)

        for i in range(0, markerSetCount):
            # Model name
            modelName, separator, remainder = bytes(data[offset:]).partition(b'\0')
            offset += len(modelName) + 1
            trace("Model Name:", modelName.decode('utf-8'))

            # Marker count (4 bytes)
            markerCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            trace("Marker Count:", markerCount)

            for j in range(0, markerCount):
                pos = Vector3.unpack(data[offset:offset + 12])
                offset += 12
                # trace( "\tMarker", j, ":", pos[0],",", pos[1],",", pos[2] )

        # Unlabeled markers count (4 bytes)
        unlabeledMarkersCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("Unlabeled Markers Count:", unlabeledMarkersCount)

        for i in range(0, unlabeledMarkersCount):
            pos = Vector3.unpack(data[offset:offset + 12])
            offset += 12
            trace("\tMarker", i, ":", pos[0], ",", pos[1], ",", pos[2])

        # Rigid body count (4 bytes)
        rigidBodyCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("Rigid Body Count:", rigidBodyCount)

        for i in range(0, rigidBodyCount):
            offset += self.__unpackRigidBody(data[offset:])

        # Version 2.1 and later
        skeletonCount = 0
        if ((self.__natNetStreamVersion[0] == 2 and self.__natNetStreamVersion[1] > 0) or self.__natNetStreamVersion[
            0] > 2):
            skeletonCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            trace("Skeleton Count:", skeletonCount)
            for i in range(0, skeletonCount):
                offset += self.__unpackSkeleton(data[offset:])

        # Labeled markers (Version 2.3 and later)
        labeledMarkerCount = 0
        if ((self.__natNetStreamVersion[0] == 2 and self.__natNetStreamVersion[1] > 3) or self.__natNetStreamVersion[
            0] > 2):
            labeledMarkerCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            trace("Labeled Marker Count:", labeledMarkerCount)
            for i in range(0, labeledMarkerCount):
                id = int.from_bytes(data[offset:offset + 4], byteorder='little')
                offset += 4
                pos = Vector3.unpack(data[offset:offset + 12])
                offset += 12
                size = FloatValue.unpack(data[offset:offset + 4])
                offset += 4

                # Version 2.6 and later
                if ((self.__natNetStreamVersion[0] == 2 and self.__natNetStreamVersion[1] >= 6) or
                        self.__natNetStreamVersion[0] > 2 or major == 0):
                    param, = struct.unpack('h', data[offset:offset + 2])
                    offset += 2
                    occluded = (param & 0x01) != 0
                    pointCloudSolved = (param & 0x02) != 0
                    modelSolved = (param & 0x04) != 0

        # Force Plate data (version 2.9 and later)
        if ((self.__natNetStreamVersion[0] == 2 and self.__natNetStreamVersion[1] >= 9) or self.__natNetStreamVersion[
            0] > 2):
            forcePlateCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            trace("Force Plate Count:", forcePlateCount)
            for i in range(0, forcePlateCount):
                # ID
                forcePlateID = int.from_bytes(data[offset:offset + 4], byteorder='little')
                offset += 4
                trace("Force Plate", i, ":", forcePlateID)

                # Channel Count
                forcePlateChannelCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
                offset += 4

                # Channel Data
                for j in range(0, forcePlateChannelCount):
                    trace("\tChannel", j, ":", forcePlateID)
                    forcePlateChannelFrameCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
                    offset += 4
                    for k in range(0, forcePlateChannelFrameCount):
                        forcePlateChannelVal = int.from_bytes(data[offset:offset + 4], byteorder='little')
                        offset += 4
                        trace("\t\t", forcePlateChannelVal)

        # Latency
        latency, = FloatValue.unpack(data[offset:offset + 4])
        offset += 4

        # Timecode
        timecode = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        timecodeSub = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        # Timestamp (increased to double precision in 2.7 and later)
        if ((self.__natNetStreamVersion[0] == 2 and self.__natNetStreamVersion[1] >= 7) or self.__natNetStreamVersion[
            0] > 2):
            timestamp, = DoubleValue.unpack(data[offset:offset + 8])
            offset += 8
        else:
            timestamp, = FloatValue.unpack(data[offset:offset + 4])
            offset += 4

        # Frame parameters
        param, = struct.unpack('h', data[offset:offset + 2])
        isRecording = (param & 0x01) != 0
        trackedModelsChanged = (param & 0x02) != 0
        offset += 2
        '''
        # Send information to any listener.
        if self.newFrameListener is not None:
            self.newFrameListener( frameNumber, markerSetCount, unlabeledMarkersCount, rigidBodyCount, skeletonCount,
                                  labeledMarkerCount, latency, timecode, timecodeSub, timestamp, isRecording, trackedModelsChanged )
        '''

    # Unpack a marker set description packet
    def __unpackMarkerSetDescription(self, data):
        offset = 0

        name, separator, remainder = bytes(data[offset:]).partition(b'\0')
        offset += len(name) + 1
        trace("Markerset Name:", name.decode('utf-8'))

        markerCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        for i in range(0, markerCount):
            name, separator, remainder = bytes(data[offset:]).partition(b'\0')
            offset += len(name) + 1
            trace("\tMarker Name:", name.decode('utf-8'))

        return offset

    # Unpack a rigid body description packet
    def __unpackRigidBodyDescription(self, data):
        offset = 0

        # Version 2.0 or higher
        if (self.__natNetStreamVersion[0] >= 2):
            name, separator, remainder = bytes(data[offset:]).partition(b'\0')
            offset += len(name) + 1
            trace("\tMarker Name:", name.decode('utf-8'))

        id = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        parentID = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        timestamp = Vector3.unpack(data[offset:offset + 12])
        offset += 12

        return offset

    # Unpack a skeleton description packet
    def __unpackSkeletonDescription(self, data):
        offset = 0

        name, separator, remainder = bytes(data[offset:]).partition(b'\0')
        offset += len(name) + 1
        trace("\tMarker Name:", name.decode('utf-8'))

        id = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        rigidBodyCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        for i in range(0, rigidBodyCount):
            offset += self.__unpackRigidBodyDescription(data[offset:])

        return offset

    # Unpack a data description packet
    def __unpackDataDescriptions(self, data):
        offset = 0
        datasetCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        for i in range(0, datasetCount):
            type = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            if (type == 0):
                offset += self.__unpackMarkerSetDescription(data[offset:])
            elif (type == 1):
                offset += self.__unpackRigidBodyDescription(data[offset:])
            elif (type == 2):
                offset += self.__unpackSkeletonDescription(data[offset:])

    def __dataThreadFunction(self, socket):
        while True:
            # Block for input
            data, addr = socket.recvfrom(32768)  # 32k byte buffer size
            if (len(data) > 0):
                self.__processMessage(data)

    def __processMessage(self, data):
        trace("Begin Packet\n------------\n")

        messageID = int.from_bytes(data[0:2], byteorder='little')
        trace("Message ID:", messageID)

        packetSize = int.from_bytes(data[2:4], byteorder='little')
        trace("Packet Size:", packetSize)

        offset = 4
        if (messageID == self.NAT_FRAMEOFDATA):
            self.__unpackMocapData(data[offset:])
        elif (messageID == self.NAT_MODELDEF):
            self.__unpackDataDescriptions(data[offset:])
        elif (messageID == self.NAT_PINGRESPONSE):
            offset += 256  # Skip the sending app's Name field
            offset += 4  # Skip the sending app's Version info
            self.__natNetStreamVersion = struct.unpack('BBBB', data[offset:offset + 4])
            offset += 4
        elif (messageID == self.NAT_RESPONSE):
            if (packetSize == 4):
                commandResponse = int.from_bytes(data[offset:offset + 4], byteorder='little')
                offset += 4
            else:
                message, separator, remainder = bytes(data[offset:]).partition(b'\0')
                offset += len(message) + 1
                trace("Command response:", message.decode('utf-8'))
        elif (messageID == self.NAT_UNRECOGNIZED_REQUEST):
            trace("Received 'Unrecognized request' from server")
        elif (messageID == self.NAT_MESSAGESTRING):
            message, separator, remainder = bytes(data[offset:]).partition(b'\0')
            offset += len(message) + 1
            trace("Received message from server:", message.decode('utf-8'))
        else:
            trace("ERROR: Unrecognized packet type")

        trace("End Packet\n----------\n")

    def sendCommand(self, command, commandStr, socket, address):
        # Compose the message in our known message format
        if (command == self.NAT_REQUEST_MODELDEF or command == self.NAT_REQUEST_FRAMEOFDATA):
            packetSize = 0
            commandStr = ""
        elif (command == self.NAT_REQUEST):
            packetSize = len(commandStr) + 1
        elif (command == self.NAT_PING):
            commandStr = "Ping"
            packetSize = len(commandStr) + 1

        data = command.to_bytes(2, byteorder='little')
        data += packetSize.to_bytes(2, byteorder='little')

        data += commandStr.encode('utf-8')
        data += b'\0'

        socket.sendto(data, address)

    def run(self):
        # Create the data socket
        self.dataSocket = self.__createDataSocket(self.dataPort)
        if (self.dataSocket is None):
            print("Could not open data channel")
            exit

        # Create the command socket
        self.commandSocket = self.__createCommandSocket()
        if (self.commandSocket is None):
            print("Could not open command channel")
            exit

        # Create a separate thread for receiving data packets
        dataThread = Thread(target=self.__dataThreadFunction, args=(self.dataSocket,))
        dataThread.start()

        # Create a separate thread for receiving command packets
        commandThread = Thread(target=self.__dataThreadFunction, args=(self.commandSocket,))
        commandThread.start()

        self.sendCommand(self.NAT_REQUEST_MODELDEF, "", self.commandSocket, (self.serverIPAddress, self.commandPort))
