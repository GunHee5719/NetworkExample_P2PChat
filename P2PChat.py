# 20154983 Jang Gun Hee
# P2PChat.py

from socket import *
import sys
import time
import threading
import json

serverName = "nsl2.cau.ac.kr"
portList = [24983, 34983, 44983, 54983]

nodeID = 0
nickname = ""

incomingNum = 0
outgoingNum = 0

incomingList = []
outgoingList = []

temp = 0
requestFlag1 = 0
requestFlag2 = 0
myMessage = ""
responseMessage = ""


def myTimer():
    global requestFlag1
    global requestFlag2
    global responseMessage

    firstTime = 0
    while True:
        time.sleep(0.01)

        if requestFlag1 == 1:
            if requestFlag2 == 0:
                firstTime = time.time()
                requestFlag2 = 1
            else:
                if (time.time() - firstTime) > 5:
                    responseMessage = "No Reply"
                    print(">> No Reply from node <", (temp + 1), ">")
                    firstTime = 0
                    requestFlag1 = 0
                    requestFlag2 = 0


def waitResponse():
    global myMessage
    global responseMessage
    global outgoingList
    global incomingList
    global outgoingNum
    global incomingNum
    global temp
    global requestFlag1
    global requestFlag2
    global clientSocket
    global serverSocket

    while True:
        responseMessage, address = serverSocket.recvfrom(2048)

        if responseMessage == "Connection OK":
            print(">> Connected with node <", (temp + 1), ">")
            outgoingList.append(temp)
            outgoingNum += 1
            requestFlag1 = 0
            requestFlag2 = 0

        elif responseMessage == "Connection NOK":
            requestFlag1 = 0
            requestFlag2 = 0
            print(">> Connection refused from node <", (temp + 1), ">")

        elif responseMessage == "Request Connection":
            if incomingNum > 2:
                myMessage = "Connection NOK"
            else:
                myMessage = "Connection OK"
                incomingList.append(temp)
                incomingNum += 1

            clientSocket.sendto(myMessage.encode(), (serverName, portList[temp-1]))


# Check the arguments for nickname.
if len(sys.argv) < 3:
    print(">> Put your nodeID and nickname by arguments.")
    print("")
    sys.exit(0)
elif len(sys.argv) > 3:
    print(">> Your nickname cannot include space.")
    print("")
    sys.exit(0)
elif len(sys.argv[2]) > 64:
    print(">> Your nickname length cannot exceed 64 bytes.")
    print("")
    sys.exit(0)
elif sys.argv[2].isalpha() is False:
    print(">> Your nickname should consist of English, cannot include special character.")
    print("")
    sys.exit(0)
elif int(sys.argv[1]) > 4:
    print(">> NodeID should in range 1~4.")
    print("")
    sys.exit(0)
elif int(sys.argv[1]) < 1:
    print(">> NodeID should in range 1~4.")
    print("")
    sys.exit(0)
else:
    nickname = sys.argv[2]
    nodeID = int(sys.argv[1])

serverPort = portList[nodeID - 1]
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

clientSocket = socket(AF_INET, SOCK_DGRAM)

print("Welcome <", nickname, "> to P2P chat room at node <", nodeID, "> , serverPort <", serverPort, ">")

t1 = threading.Thread(target=myTimer, args=())
t1.daemon = True
t1.start()

t2 = threading.Thread(target=waitResponse, args=())
t2.daemon = True
t2.start()

try:
    while True:
        if temp >= 4:
            break

        if temp == (nodeID - 1):
            temp += 1
        else:
            myMessage = "Request Connection"
            clientSocket.sendto(myMessage.encode(), (serverName, portList[temp]))

            requestFlag1 = 1
            while True:
                time.sleep(0.01)
                if requestFlag1 == 0:
                    break

            temp += 1

            if outgoingNum > 2:
                break

    while True:
        time.sleep(0.01)

except KeyboardInterrupt:
    print("")
    print("Bye bye~")
