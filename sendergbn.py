# // NAME: LOKESH PATIL
# // Roll Number: CS20B047
# // Course: CS3205 Jan. 2023 semester
# // Lab number: 4
# // Date of submission: 05.04.23
# // I confirm that the source file is entirely written by me without
# // resorting to any dishonest means.

import sys
import threading
import time
import socket
import multiprocessing
import os


# create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# define the server address
port_no = 12345
server_address = ('localhost', port_no)

pkt_len = int(512)
pkt_rate = int(5)
MAX_BUFFER_SIZE = int(10)
buffer_size = MAX_BUFFER_SIZE
max_pkts = int(20)
window_size = int(3)
RTT_ave = None
buffer = [] #gloabl temp buffer
Dict_sent = {} # stores time at which data pkt of a seq_no is sent
Dict_rec = {} # stores time at which ack is received for a seq_no
timeout = float(5)
acks = [] # array of seq_nos of packets acked till now
window = []
exit_value = int(0)
debug = int(0)
no_of_attempts = {}
seq_no = int(0)
lock = threading.Lock()
sum1 = float(0)

def update_timeout():  #updates the timeout after sending 10 pkts
    global RTT_ave
    sum = float(0)
    for ack in acks:
        RTT = Dict_rec[ack] - Dict_sent[ack]
        sum = sum + RTT
    RTT_ave = sum/(len(acks))
    global timeout
    timeout = RTT_ave*2
    


def transmit_element(packet): #tranmits elements to the receiver   
    global sum1
    ele = int.from_bytes(packet[:2], byteorder='big')
    print("Transmitting data pkt with seqNo: ")
    print(int.from_bytes(packet[:2], byteorder='big'))
    print("\n")
    ele = int(ele)
    Dict_sent[ele] = time.time()
    client_socket.sendto(packet, server_address)
    no_of_attempts.setdefault(ele, 0)
    no_of_attempts[ele] = no_of_attempts[ele] + 1
    sum1 = sum1 + 1
    if no_of_attempts[ele]>5:  #if no of attemps for a packet exceed 5 then terminate the program of sender
        global exit_value
        exit_value = 1
        return
    if len(acks)>10:
        update_timeout()

def transmit_window():  #window gets trasmitted
    for i in range (len(window)):
        transmit_element(window[i])

def update_window():
    while len(buffer) != 0:
        if len(window) == window_size:
            break
        ele = buffer[0]
        window.append(ele)
        buffer.reverse()
        buffer.pop()
        buffer.reverse()

def slide_window(): #slides window by one after successfully receiving ack for the start of window element
    global buffer
    if len(window) == window_size:
        window.pop(0)

        while len(buffer) == 0:
            if len(buffer)>0:
                break
            
            time.sleep(0.001)
        ele = buffer[0]
        window.append(buffer[0])
        buffer.pop(0)
        transmit_element(ele)
        

def update_acks(ok):  #looping function that takes care of receiving acks and carrying out further steps
    print("we are in update ACK\n")
    data, server_address = client_socket.recvfrom(4096)
    ele = int.from_bytes(data[:2], byteorder='big')
    print("ACK received for packet no: ")
    print(ele)
    print("\n")
    if ele == 1000:     #represent negative ack that means packet is dropped
        transmit_window()
        return
    Dict_rec[ele] = time.time()
    global debug
    if debug == int(1):
        x= float("{:.2f}".format((Dict_rec[ele] - Dict_sent[ele])))
        print("Seq #: "+ str(ele) + " Time generated: "+ str(float("{:.2f}".format(Dict_sent[ele]))) + " RTT: "+ str(x) + " Number of attempts: "+ str(no_of_attempts[ele])+ "\n")

    if (Dict_rec[ele] - Dict_sent[ele]) > timeout:
        transmit_window()
    else:
        acks.append(ele)
        global exit_value
        if len(acks) == max_pkts:
            exit_value = 1
            return
        slide_window()

def add_to_buffer():    
    global seq_no
    if len(buffer)<buffer_size:

        print("Adding to buffer seqNo: ")
        print(seq_no)
        print("\n")

        buffer.append(seq_no)
        seq_no = seq_no + 1
    else:
        update_acks(0)



class Sender:  # sender classs to launch thread for generating packets at regular interval
    def __init__(self, packet_length, packet_gen_rate, max_buffer_size):
        self.packet_length = packet_length
        self.packet_gen_rate = packet_gen_rate
        self.max_buffer_size = MAX_BUFFER_SIZE
        self.buffer = []
        self.seq_num = int(0)
        self.lock = threading.Lock()

        # start a thread to generate packets
        self.packet_thread = threading.Thread(target=self.generate_packets)
        self.packet_thread.daemon = True
        self.packet_thread.start()

    def generate_packets(self):  # generate packets with pkt_rate 
        global buffer
        while True:
            # check if buffer is full
            if len(buffer) < self.max_buffer_size:
                # generate a new packet
                packet = bytearray(self.packet_length)
                packet[:2] = self.seq_num.to_bytes(2, byteorder='big')
                # add the packet to the buffer
                print("Adding pkt to buffer with seq #:" + str(self.seq_num))
                with self.lock:
                    self.buffer.append(packet)
                    buffer.append(packet)
                    self.seq_num += 1
            else:
                print("Buffer full, dropping packet")
            # wait for the specified time before generating the next packet
            time.sleep(1 / self.packet_gen_rate)

    def get_packet(self):  #removes top pkt from buffer when required
        with self.lock:
            if self.buffer:
                # remove the oldest packet from the buffer and return it
                self.buffer.pop(0)
                return buffer.pop(0)
            else:
                return None

if __name__ == '__main__':

    list = sys.argv
    receiver_name = None
    idx = None
    if list[1]=='-d':
        idx = int(1)
        debug = int(1)
    else:
        idx= int(0)
    
    receiver_name = list[idx+2]
    port_no = list[idx+4]
    pkt_len = int(list[idx+6])
    pkt_rate = int(list[idx+8])
    max_pkts = int(list[idx+10])
    window_size = int(list[idx+12])
    MAX_BUFFER_SIZE = int(list[idx+14])
    buffer_size = MAX_BUFFER_SIZE

    sender = Sender(pkt_len, pkt_rate, buffer_size)

    # loop to get packets from the sender and send them in window to the receiver
    while len(window)!=window_size:
        packet = sender.get_packet()
        if packet == None:
            # print(f"Sending packet with sequence number {int.from_bytes(packet[:2], byteorder='big')}")
            # wait for a short time if the buffer is empty
            time.sleep(0.001)
        else:
            # do something with the packet
            # i = {int.from_bytes(packet[:2], byteorder='big')}
            window.append(packet)
            # print(f"Sending packet with sequence number {int.from_bytes(packet[:2], byteorder='big')}")
            # transmit_element(i)

    transmit_window()
    while True: #loop to receive ack packets from receiver
        update_acks(0)
        if exit_value == 1:
            break
    print("Packet generation rate: "+ str(pkt_rate))
    print("Packet length: "+ str(pkt_len))
    sum2 = len(acks)
    ratio = float(sum1/sum2)
    print("Retransmission Ratio: "+ str(float("{:.2f}".format(ratio))))
    sum = float(0)
    for ack in acks:
        RTT = Dict_rec[ack] - Dict_sent[ack]
        sum = sum + RTT
    RTT_ave = sum/(len(acks))
    print("Average RTT value: "+ str(RTT_ave))



        

