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

seq_list = [0, 0, 0, 0]

temp = 0
requestFlag1 = 0
requestFlag2 = 0
inputFlag = 0
clientState = 0
needReconnect = 0
myMessage = ""
responseMessage = ""

mySequenceNumber = 0


def myTimer():
    global requestFlag1
    global requestFlag2

    firstTime = 0
    while True:
        time.sleep(0.01)

        if requestFlag1 == 1:
            if requestFlag2 == 0:
                firstTime = time.time()
                requestFlag2 = 1
            else:
                if (time.time() - firstTime) > 5:
                    print(">> No Reply from node <", (temp + 1), ">")
                    firstTime = 0
                    requestFlag1 = 0
                    requestFlag2 = 0

def myTimer2():
    global needReconnect
    global inputFlag
    global temp
    global requestFlag1

    while True:
        time.sleep(0.01)
        if needReconnect > 0:
            time.sleep(1)
            # For reconnectiong
            print("")
            print(">> Reconnecting... You Can not use chatting until connecting finished.")
            inputFlag = 1
            temp = 0
            while True:
                if temp >= 4:
                    break

                if outgoingNum >= 2:
                    break

                alreadyConnected = 0
                for a in range(len(outgoingList)):
                    if outgoingList[a] == temp:
                        alreadyConnected = 1
                for b in range(len(incomingList)):
                    if incomingList[b] == temp:
                        alreadyConnected = 1

                if temp == nodeID:
                    temp += 1
                elif alreadyConnected == 1:
                    temp += 1
                else:
                    myMessage = "Request Connection"
                    myJson = {"myMessage": myMessage, "content": "null", "nodeID": nodeID, "seq": "null",
                              "nickname": "null",
                              "from": "null"}
                    clientSocket.sendto(json.dumps(myJson).encode(), (serverName, portList[temp]))

                    requestFlag1 = 1
                    while True:
                        time.sleep(0.01)
                        if requestFlag1 == 0:
                            break

                    temp += 1

            print(">> Finish Reconnection! Use Chatting.")
            print("")
            needReconnect=0
            inputFlag = 0


def waitInput():
    global mySequenceNumber
    global clientState

    while True:
        myInput = input("")

        if inputFlag == 1:
            print(">> Please wait for connecting.")

        elif myInput == "\connection":
            print(" [Connection List]")
            serverAddress = serverSocket.getsockname()
            for i in range(len(outgoingList)):
                print("   < Node >", (outgoingList[i] + 1), " < IP >", serverAddress[0], " < Port >",
                      portList[outgoingList[i]], " < Connection > outgoing")
            for j in range(len(incomingList)):
                print("   < Node >", (incomingList[j] + 1), " < IP >", serverAddress[0], " < Port >",
                      portList[incomingList[j]], " < Connection > incoming")

        elif myInput == "\quit":
            print("")
            print("Bye bye~")

            mySequenceNumber += 1
            seq_list[nodeID] += 1
            myJson = {"myMessage": "quit", "content": "null", "nodeID": nodeID, "seq": mySequenceNumber,
                      "nickname": nickname, "from": nodeID}
            for a in range(len(outgoingList)):
                clientSocket.sendto(json.dumps(myJson).encode(), (serverName, portList[outgoingList[a]]))
            for b in range(len(incomingList)):
                clientSocket.sendto(json.dumps(myJson).encode(), (serverName, portList[incomingList[b]]))

            clientState = 1
            break

        else:
            myMessage = "talk"
            content = myInput

            mySequenceNumber += 1
            seq_list[nodeID] += 1
            myJson = {"myMessage": myMessage, "content": content, "nodeID": nodeID, "seq": mySequenceNumber,
                      "nickname": nickname, "from": nodeID}

            for k in range(len(outgoingList)):
                clientSocket.sendto(json.dumps(myJson).encode(), (serverName, portList[outgoingList[k]]))
            for l in range(len(incomingList)):
                clientSocket.sendto(json.dumps(myJson).encode(), (serverName, portList[incomingList[l]]))


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
    global inputFlag
    global needReconnect
    global clientSocket
    global serverSocket

    while True:
        myJson, address = serverSocket.recvfrom(2048)

        myJson = myJson.decode()
        myData = json.loads(myJson)

        responseMessage, content, src_node, src_nick, seq, fromwhere = myData.get("myMessage"), myData.get(
            "content"), myData.get("nodeID"), myData.get("nickname"), myData.get("seq"), myData.get("from")

        # When this client requested to other node for connection, this is one case of the node's response.
        if responseMessage == "Connection OK":
            if temp <=3:
                print(">> Connected with node <", (temp + 1), ">")
                outgoingList.append(temp)
                outgoingNum += 1
                requestFlag1 = 0
                requestFlag2 = 0

        # When this client requested to other node for connection, this is one case of the node's response.
        elif responseMessage == "Connection NOK":
            requestFlag1 = 0
            requestFlag2 = 0
            print(">> Connection refused from node <", (temp + 1), ">")

        # When this client requested from other node for connection, this client will response in this line if it is running.
        elif responseMessage == "Request Connection":
            seq_list[src_node] = 0
            if incomingNum >= 2:
                myMessage = "Connection NOK"

            elif (incomingNum + outgoingNum) >= 3:
                myMessage = "Connection NOK"

            else:
                myMessage = "Connection OK"
                incomingList.append(src_node)
                incomingNum += 1

            myJson = {"myMessage": myMessage, "content": "null", "nodeID": nodeID, "seq": "null", "nickname": "null",
                      "from": "null"}
            clientSocket.sendto(json.dumps(myJson).encode(), (serverName, portList[src_node]))

        elif responseMessage == "quit":
            if seq > seq_list[src_node]:
                needReconnect = 0

                seq_list[src_node] += 1
                print(">> ",src_nick," quitted.","  ( node",(src_node+1),", seq",seq,", from",(fromwhere+1),")")

                myJson = {"myMessage": "quit", "content": "null", "nodeID": src_node, "seq": seq,
                          "nickname": src_nick, "from": nodeID}
                for k in range(len(outgoingList)):
                    if outgoingList[k] == src_node:
                        print(">> Connection Closed.")
                        needReconnect = 1
                    if outgoingList[k] != fromwhere:
                        clientSocket.sendto(json.dumps(myJson).encode(), (serverName, portList[outgoingList[k]]))
                for l in range(len(incomingList)):
                    if incomingList[l] == src_node:
                        print(">> Connection Closed.")
                        needReconnect = 2
                    if incomingList[l] != fromwhere:
                        clientSocket.sendto(json.dumps(myJson).encode(), (serverName, portList[incomingList[l]]))

                if needReconnect == 1:
                    outgoingList.pop(outgoingList.index(src_node))
                    outgoingNum -= 1
                elif needReconnect == 2:
                    incomingList.pop(incomingList.index(src_node))
                    incomingNum -= 1



        elif responseMessage == "talk":
            # Check if this message is already received. If it is, this message will be discarded.
            if seq > seq_list[src_node]:
                seq_list[src_node] += 1
                print("[", src_nick, "]", content, "  ( node", (src_node + 1), ", seq", seq, ", from", (fromwhere + 1),
                      ")")

                myJson = {"myMessage": "talk", "content": content, "nodeID": src_node, "seq": seq,
                          "nickname": src_nick, "from": nodeID}
                for k in range(len(outgoingList)):
                    if outgoingList[k] != fromwhere:
                        clientSocket.sendto(json.dumps(myJson).encode(), (serverName, portList[outgoingList[k]]))
                for l in range(len(incomingList)):
                    if incomingList[l] != fromwhere:
                        clientSocket.sendto(json.dumps(myJson).encode(), (serverName, portList[incomingList[l]]))


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
    nodeID = int(sys.argv[1]) - 1

serverPort = portList[nodeID]
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('nsl2.cau.ac.kr', serverPort))

clientSocket = socket(AF_INET, SOCK_DGRAM)

print("Welcome <", nickname, "> to P2P chat room at node <", (nodeID + 1), "> , serverPort <", serverPort, ">")

t1 = threading.Thread(target=myTimer, args=())
t1.daemon = True
t1.start()

t2 = threading.Thread(target=waitResponse, args=())
t2.daemon = True
t2.start()

t3 = threading.Thread(target=waitInput, args=())
t3.daemon = True
t3.start()

t4 = threading.Thread(target=myTimer2, args=())
t4.daemon = True
t4.start()

temp = 0
try:
    # For connecting
    print("")
    print(">> Connecting...")
    inputFlag = 1
    while True:
        if temp >= 4:
            break

        if outgoingNum >= 2:
            break

        if temp == nodeID:
            temp += 1
        else:
            myMessage = "Request Connection"
            myJson = {"myMessage": myMessage, "content": "null", "nodeID": nodeID, "seq": "null", "nickname": "null",
                      "from": "null"}
            clientSocket.sendto(json.dumps(myJson).encode(), (serverName, portList[temp]))

            requestFlag1 = 1
            while True:
                time.sleep(0.01)
                if requestFlag1 == 0:
                    break

            temp += 1

    print(">> Finish Connection! Use Chatting.")
    print("")
    inputFlag = 0
    while True:
        time.sleep(0.01)

        if clientState == 1:
            break

except KeyboardInterrupt:
    print("")
    print("Bye bye~")

    mySequenceNumber += 1
    seq_list[nodeID] += 1
    myJson = {"myMessage": "quit", "content": "null", "nodeID": nodeID, "seq": mySequenceNumber,
              "nickname": nickname, "from": nodeID}
    for a in range(len(outgoingList)):
        clientSocket.sendto(json.dumps(myJson).encode(), (serverName, portList[outgoingList[a]]))
    for b in range(len(incomingList)):
        clientSocket.sendto(json.dumps(myJson).encode(), (serverName, portList[incomingList[b]]))
