# 20154983 Jang Gun Hee
# P2PChat.py

from socket import *
import sys
import time
import threading

serverName = "nsl2.cau.ac.kr"
serverPort = 0
nodeID = 0
nickname = ""
clientSocket = socket(AF_INET, SOCK_DGRAM)

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
elif sys.argv[1] > 4:
    print(">> NodeID should in range 1~4.")
    print("")
    sys.exit(0)
elif sys.argv[1] < 1:
    print(">> NodeID should in range 1~4.")
    print("")
    sys.exit(0)
else:
    nickname = sys.argv[2]
    nodeID = sys.argv[1]

print(">> ",nickname," ",nodeID)

# if nodeID == 1:
#     serverPort =
#
# try:
#     while True:
#
#
# except KeyboardInterrupt:
#     print("")
#     print("Bye bye~")
#     mymessage = "6"
#     clientSocket.sendto(mymessage.encode(), (serverName, serverPort))
