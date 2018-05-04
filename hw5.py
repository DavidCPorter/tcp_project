"""
Where solution code to HW5 should be written.  No other files should
be modified.
"""

import socket
import io
import time
import typing
import struct
import homework5
import homework5.logging
import pdb
import sys
import math


rtt = .2
HEADERSIZE = 1
FIN = b'\x01\x01'
BUFFER = 40

# SO I TRIED TO FIX MY PROBLEM WITH THE MOD 255 BY ONLY MODING THE MOMENT BEFORE YOU SEND SEQUENCE OVER THE WIRE OTHER THAN THAT, WE'RE USING THE TOTAL SEQUENCE FOR THE LOGIC ELSEWHERE. No longer need to track data_cycles aka sequence number 256 cycles

def send(sock: socket.socket, data: bytes):
    """
    Implementation of the sending logic for sending data over a slow,
    lossy, constrained network.

    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.
        data -- A bytes object, containing the data to send over the network.
    """

    logger = homework5.logging.get_logger("hw5-wire")
    #packet_size is the size of the packet_data so max size minus header
    packet_data_size = homework5.MAX_PACKET-HEADERSIZE
    pause = .5
    window = homework5.MAX_PACKET*BUFFER-BUFFER

    offset_window = range(0, len(data), window)
    offset_packet = range(0, window, homework5.MAX_PACKET-HEADERSIZE)
    et = 1
    dt =0
    ti=1
    # initialize
    sequence_dropped = 0

    total_sequences = math.ceil(len(data)/packet_data_size)

    while True:

    #function to send packets according to where the sliding window is
    #dont need the offset anymore because the handle response will return the sequence to send from
        #print("THIS IS sequence_dropped->")
        #print(sequence_dropped)
        #print("THIS IS total_sequences->")
        #print(total_sequences)

        #print("this is data cycle", DATA_CYCLES)
        #print("this is packet_data_size", packet_data_size)
        #print("this is data length", len(data))
        #print("this is window", window)
        window_data = data[sequence_dropped * packet_data_size : sequence_dropped * packet_data_size + window]
        offset_packet = range(0, len(window_data), homework5.MAX_PACKET-HEADERSIZE)
        #print("OFFSET PACKET____")
        #print(offset_packet)
        #print(len(offset_packet))
        #we want to return total sequence
        sequence_dropped,et,dt,ti = package_data_to_send(sock,et,dt, sequence_dropped, window_data, packet_data_size, offset_packet,ti)
        print(sequence_dropped, total_sequences)

        #if this is true, means all data has been sent so you can send FIN
        if sequence_dropped > total_sequences-1:
            count =0
            while True:
                count+=1
                sock.send(FIN)
                try:
                    final = sock.recv(2)
                    print("FINAL n FIN->", final, FIN)
                    if final == FIN:
                        sock.close()
                        print('CLOSED SUCCESSFULLY')
                        break
                    else:
                        print("STILL DATA IN PIPE")
                        sock.settimeout(.01)
                        while sock.recv(1):
                            continue
                        continue

                except socket.timeout:
                    if count >3:
                        #print("SENT FIN ENOUGH TIMES")
                        sock.close()
                    #print("FIN TIMEOUT"*10)
                    break

            break

def package_data_to_send(sock, et, dt, start_sequence_num, window_data, packet_data_size, offset_packet, ti):
    #get sequence number to send which is start_sequence mod 255
    sequence = start_sequence_num
    start_times= {}
    for packet_data in [window_data[i:i + packet_data_size] for i in offset_packet]:
        packet = create_packet(sequence, packet_data)
        print("PACKET->", len(packet))
        print("\nSENDER SENDING SEQUENCE ->", sequence)
        print(ti)
        start_times[sequence%256] = time.time()
        sock.send(packet)
        sock.settimeout(ti)
        # if sequence == 255:
        #     DATA_CYCLES +=1
        #     sequence = 0
        # else:
        sequence +=1

    sequence_dropped,et,dt = handle_response(sock,et,dt,start_times,start_sequence_num, offset_packet)
    ti = calculate_timeout(et, dt)


    return sequence_dropped,et,dt,ti



def create_packet(sequence,data):
    sequence = sequence_to_bytes(sequence)
    chunk = sequence+data
    return chunk

def sequence_to_bytes(sequence):
    sequence = bytes([sequence%256])
    # sequence_string = '0x'+sequence.hex()
    # hex_int = int(sequence_string, base=16)
    # sequence_string = hex(hex_int+1)[2:]
    # sequence = bytes.fromhex(sequence_string)
    return sequence

def calculate_timeout(et, dt):
    #estimated RTT + (devation of RTT *4)
    return et + (dt*4)


def handle_response(sock, et, dt, start_times, sequence_start, offset_packet):
    return_sequence = None
    #sequence start is total sequence not mod 255
    check_sequence = sequence_start
    #to check recv we have to mod 255 the sequence number
    count_add = 0
    sequence_start = sequence_start%256
    while True:
        try:
            print("SEQUENCE NUMBER WERE LOOKING TO MATCH HEADER ->", sequence_start)
            print("SEQUENCE NUMBER FOR COMPLETE ROUND ->", (check_sequence+len(offset_packet))%256)
            #if true, we've reached the end of the window
            if sequence_start == (check_sequence+len(offset_packet))%256:
                # sequence_start = check_sequence+sequence_start
                #return original sequence number + sequences verified from receiver with other rtt stuff
                return check_sequence+count_add,et,dt
            header = sock.recv(1)
            print('this is header->', int.from_bytes(header, byteorder=sys.byteorder))
            #print('\n')
            if header == bytes([sequence_start]):
                finish = time.time()
                #print (start_times)
                if  sequence_start in start_times:
                    rtt = finish-start_times[sequence_start]

                else:
                    print("NOT IN START TIME")
                    rtt = .04
                # rtt = .04
                if sequence_start == 255:
                    sequence_start = 0
                    count_add +=1

                else:
                    sequence_start+=1
                    count_add +=1

                et = (.875*et)+.125*(rtt)
                dt = (.75*dt)+.25*abs(rtt-et)
                continue

            elif header == FIN:
                return_sequence = FIN
                break

            else:
                time.sleep(.001)
                #it's ok to shorten timeout before this buffer clearing process cuz it's resetting upon returning to caller and all data should be in the buffer already. we don't want to wait for a long timeout here.
                sock.settimeout(.01)
                while sock.recv(1):
                    continue
                #print("wrong header ->", header)
                #print("should be->", sequence_start)
                #gotta return original sequence number plus the number of confirmed receipts
                return_sequence = check_sequence+count_add
                break

        except socket.timeout:
            print("TIMEOUTT"+'1'*10)
            # time.sleep(.001)
            # while sock.recv(1):
            #     continue
            #gotta return original sequence number plus the number of confirmed receipts
            return_sequence = check_sequence+count_add
            break

    return return_sequence,et,dt



def recv(sock: socket.socket, dest: io.BufferedIOBase) -> int:
    """
    Implementation of the receiving logic for receiving data over a slow,
    lossy, constrained network.

    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.

    Return:
        The number of bytes written to the destination.
    """
    logger = homework5.logging.get_logger("hw5-receiver")
    num_bytes = 0
    sequence = 0
    count = 0
    while True:
        data = sock.recv(homework5.MAX_PACKET)
        #print("\nRECEIVER DATA[0]->", data[:2])
        if data[0] == sequence:
            sock.send(bytes([sequence]))
            #print('\n')
            print("RECEVIER SENT THESE BYTES->", str(data[0]))
            buff = data[1:]
            logger.info("Received %d bytes", len(buff))
            #print('\n')
            dest.write(buff)
            count = 0
            num_bytes += len(buff)
            dest.flush()
            if sequence == 255:
                sequence = 0
            else:
                sequence+=1
            continue

        elif data[:2] == FIN:
            sock.send(FIN)
            # print("RECV CLOSED SUCCESSFULLY")
            sock.close()
            break

        if data[0] != sequence:
            # sequence-=1
            # if count ==0:
            sock.send(bytes([data[0]]))
            print("WRONG SEQUENCE -- RECEVIER GOT THESE BYTES->", str(data[0]))
            print("looking for these bytes->",sequence)


                # count+=1
            # sock.send(bytes([data[0]]))
            # print("DATA was dropped I am RECIEVER and still looking for sequence",str(bytes([sequence])))
            continue

        break
    return num_bytes
