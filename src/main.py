import time
import os
import sys
import ctypes
import socket
import argparse
from prettytable import PrettyTable
from icmp_handler import create_icmp_packet
from icmp_handler import receive_icmp_reply
from display import display_statistics
from display import show_help

sent =0
received = 0
rtts = []
is_windows = False


def check_privileges():
    #Check if the script is running with admin/root privileges.
    if sys.platform == "win32":
        if not ctypes.windll.shell32.IsUserAnAdmin():
            global is_windows
            is_windows = True
    elif sys.platform in ["linux", "darwin"]:
        if os.geteuid() != 0:
            print("⚠ WARNING: This script is not running as root!")
            print("Run the script with 'sudo':\n")
            sys.exit(1)  # Stop execution

def ping(target, count=4, timeout=1, ttl=64, interface=None):
    try:
        # Resolve the target (IPv4 or IPv6)
        addr_info = socket.getaddrinfo(target, None)
        family, _, _, _, sockaddr = addr_info[0]
        dest_ip = sockaddr[0]
        ipv6 = family == socket.AF_INET6

        # Explicitly check if resolution falls back to localhost (::1 or 127.0.0.1)
        if dest_ip in ["::1", "127.0.0.1"] and target not in ["localhost", "127.0.0.1"]:
            raise socket.gaierror

    except socket.gaierror:
        print(f"Unable to resolve {target}")
        return

    print(f"Pinging {target} ({dest_ip}) with {'ICMPv6' if ipv6 else 'ICMP'} Echo Requests:")

    global  rtts
    global sent, received

    # Create raw socket
    proto = socket.IPPROTO_ICMPV6 if ipv6 else socket.IPPROTO_ICMP
    sock = socket.socket(socket.AF_INET6 if ipv6 else socket.AF_INET, socket.SOCK_RAW, proto)

    # Bind to the selected interface if specified
    if interface and sys.platform in ["linux", "darwin"] :
         if not ipv6:
             try:
                 sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, interface.encode())
             except Exception as e:
                 print(f"Error binding to interface: {e}")
                 return
         else:
             print("You cannot set network interface explicitly when pinging ipv6 networks!")
             sys.exit(1)

    table = PrettyTable(["Seq", "IP Address", "Status", "RTT (ms)"])

    for seq in range(1, count + 1):
        packet = create_icmp_packet(seq, ipv6)
        sent += 1
        sent_time = time.time()

        try:
            # Send the packet
            sock.sendto(packet, (dest_ip, 1, 0, 0) if ipv6 else (dest_ip, 1))
        except Exception as e:
            print(f"Error sending packet: {e}")
            break

        rtt = receive_icmp_reply(sock,timeout, sent_time, ipv6)

        if rtt is not None:
            received += 1
            rtts.append(rtt)
            table.add_row([seq, dest_ip, "Reply", f"{rtt:.2f}"])

        else:
            table.add_row([seq, dest_ip, "Timeout", "-"])

        os.system("cls" if os.name == "nt" else "clear")
        if is_windows: print("⚠ WARNING: If you face any issue, please re-run with Admin privileges")
        print(f"Pinging {target} ({dest_ip}) with {'ICMPv6' if ipv6 else 'ICMP'} Echo Requests:\n")
        print(table)

        time.sleep(1)

    sock.close()
    display_statistics(sent, received, rtts)

def main():
    parser = argparse.ArgumentParser(description="Custom Ping Utility with IPv6 support" , add_help=False)
    parser.add_argument("target", nargs="?")
    parser.add_argument("-c", "--count", type=int, default=4)
    parser.add_argument("-t", "--ttl", type=int, default=64)
    parser.add_argument("-i", "--interface")
    parser.add_argument("-h", "--help", action="store_true")
    args = parser.parse_args()

    if args.help or not args.target:
        show_help()

    try :
        check_privileges()
        ping(args.target, args.count)
    except KeyboardInterrupt:
        print("\nPing interrupted. Showing summary...")
        display_statistics(sent, received, rtts)


if __name__ == "__main__":
    main()