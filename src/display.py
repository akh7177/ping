import statistics
from prettytable import PrettyTable
# Function to display packet and RTT statistics
def display_statistics(sent, received,rtts):
    packet_statistics = PrettyTable(["Packet Statistics","Value"])
    loss = ((sent - received) / sent) * 100
    packet_statistics.add_row(["Sent", sent])
    packet_statistics.add_row(["Received", received])
    packet_statistics.add_row(["Lost", sent - received])
    packet_statistics.add_row(["Loss", f"{loss:.2f}%"])
    print(packet_statistics)

    if rtts:
        rtt_statistics_table = PrettyTable(["RTT Statistics","Value"])
        rtt_statistics_table.add_row(["Min RTT", f"{min(rtts):.2f} ms"])
        rtt_statistics_table.add_row(["Max RTT", f"{max(rtts):.2f} ms"])
        rtt_statistics_table.add_row(["Avg RTT", f"{sum(rtts) / len(rtts):.2f} ms"])
        rtt_statistics_table.add_row(["Std Dev RTT", f"{statistics.stdev(rtts):.2f} ms" if len(rtts) > 1 else "N/A"])
        print(rtt_statistics_table)

# Function to show help menu
def show_help():

    help_table = PrettyTable(["Option", "Description"])
    help_table.align["Option"] = "l"
    help_table.align["Description"] = "l"

    help_table.add_row(["target_ip or hostname", "Target IP or hostname to ping"])
    help_table.add_row(["-c, --count <n>", "Number of packets to send (default: 4) (optional)"])
    help_table.add_row(["-t, --ttl <n>", "Time-To-Live value (Linux/macOS on IPv4 only) (optional)"])
    help_table.add_row(["-i, --interface", "Specify network interface (Linux/macOS on IPv4 only) (optional)"])
    help_table.add_row(["-h, --help", "Show this help menu and exit"])

    print("\nCustom Ping Utility\n")
    print(help_table)
    print("\n Example Usage: python main.py 8.8.8.8 -c 4 -t 64 -i eth0\n")
    exit()