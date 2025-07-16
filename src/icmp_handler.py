import struct
import time
import select
import os
ICMP_ECHO_REQUEST = 8
ICMP6_ECHO_REQUEST = 128

def checksum(data):
    # Calculate the ICMP checksum
    if len(data) % 2:
        data += b'\x00'

    total = sum(struct.unpack("!%dH" % (len(data) // 2), data))
    total = (total >> 16) + (total & 0xFFFF)
    total += total >> 16
    return ~total & 0xFFFF

def create_icmp_packet(seq, ipv6=False):
    # Create an ICMP Echo Request packet
    pid = os.getpid() & 0xFFFF
    payload = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456'[:32]  # 32-byte payload
    if ipv6:
        header = struct.pack("!BBHHH", ICMP6_ECHO_REQUEST, 0, 0, pid, seq)
        return header + payload  # No checksum needed for ICMPv6 in raw sockets
    else:
        header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, 0, pid, seq)
        icmp_checksum = checksum(header + payload)
        header = struct.pack("!BBHHH", ICMP_ECHO_REQUEST, 0, icmp_checksum, pid, seq)
        return header + payload



def receive_icmp_reply(sock, timeout, sent_time, ipv6=False):
    #Receive and process the ICMP reply.
    while True:
        start_time = time.time()

        # Wait for a response with the given timeout
        ready = select.select([sock], [], [], timeout)
        if not ready[0]:  # Timeout reached
            return None

        recv_time = time.time()
        packet, _ = sock.recvfrom(1024)

        # Extract ICMP header


        if ipv6:
            icmp_header = packet[0:8]
            type_, code, ipv6_checksum, p_id, sequence = struct.unpack("!BBHHH", icmp_header)
        else :
            icmp_header = packet[20:28]
            type_, code, icmp_checksum, p_id, sequence = struct.unpack("!BBHHH", icmp_header)

        # Check if the reply is an ICMP Echo Reply and matches our process ID
        if (type_ == 0 or type_==129) and (p_id == (os.getpid() & 0xFFFF)):
            return (recv_time - sent_time) * 1000

        # Adjust remaining timeout
        timeout -= (time.time() - start_time)
        if timeout <= 0:
            return None