# // NAME: LOKESH PATIL
# // Roll Number: CS20B047
# // Course: CS3205 Jan. 2023 semester
# // Lab number: 4
# // Date of submission: 05.04.23
# // I confirm that the source file is entirely written by me without
# // resorting to any dishonest means.

import sys
import random
import socket
import time

# create a UDP socket
port_no = 12345
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# bind the socket to a specific address and port
server_address = ('localhost', port_no)
server_socket.bind(server_address)
client_address = None
Dict_sent = {} # stores time at which data pkt of a seq_no is sent
Dict_rec = {} # stores time at which ack is received for a seq_no
print('Server is ready to receive messages\n')

random_drop_prob = float(0.0001) #random prob for dropping packet
NFE = int(0)
max_packets = int(20)
no_of_acks = int(0)
d = int(0)
packet_length = None

def send_ack(ele): #sending ack packets to sender
    global NFE
    NFE = NFE + 1
    data = str(ele)
    print("sending ACK " + data)

    global packet_length
    ackpacket = bytearray(packet_length)
    ackpacket[:2] = ele.to_bytes(2, byteorder='big')
    server_socket.sendto(ackpacket,client_address)


def receive_packets(ele): #receives pkts from sender and decides to send ack or nack depending on pkt being dropped
    if NFE == ele:
        numberList = [0, 1]
        t = float("{:.2f}".format(time.time()))
        x = random.choices(numberList, weights=(random_drop_prob*100, 100*(1-random_drop_prob)), k=1)
        if x[0] == 1:
            global no_of_acks
            no_of_acks = no_of_acks+1
            if d == 1:
                print("Seq #: "+ str(ele) + " Time Received:"+  str(t)+ " Packet dropped: false\n")
            send_ack(ele)
            if no_of_acks>=max_packets:
                exit()
        else:
            if d == 1:
                print("Seq #: "+ str(ele) + " Time Received:"+  str(t)+ "Packet dropped: true\n")
            data = int(1000)  #represents nack
            global packet_length
            nackpacket = bytearray(packet_length)
            nackpacket[:2] = data.to_bytes(2, byteorder='big')
            server_socket.sendto(nackpacket,client_address)
    else:
        data = int(1000)  #represents nack
        nackpacket = bytearray(packet_length)
        nackpacket[:2] = data.to_bytes(2, byteorder='big')
        server_socket.sendto(nackpacket,client_address)


list = sys.argv
idx = None
if list[1]=='-d':
    idx = int(1)
    d = int(1)
else:
    idx= int(0)
port_no = list[idx+2]
max_packets = int(list[idx+4])
random_drop_prob = float(list[idx+6])



while True:
    # receive data from client
    data, client_address = server_socket.recvfrom(4096)
    packet_length = len(data)
    ele = int.from_bytes(data[:2], byteorder='big')
    print("received "+ str(ele) + " from client\n")
    receive_packets(ele)
