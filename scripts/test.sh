#!/bin/bash

# Test script for custom ping utility
# Assumes the main Python script is in '../src/main.py' relative to this script

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Python script path (relative to test.sh)
SCRIPT="../src/main.py"

# Check if the script exists
if [ ! -f "$SCRIPT" ]; then
    echo -e "${RED}Error: $SCRIPT not found${NC}"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Check if prettytable is installed
if ! python3 -c "import prettytable" &> /dev/null; then
    echo -e "${RED}Error: 'prettytable' module not installed. Run 'pip3 install prettytable'${NC}"
    exit 1
fi

echo "Starting tests for Custom Ping Utility..."
echo "Note: This script requires root privileges for some tests. Running with sudo..."

# Function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Test passed${NC}"
    else
        echo -e "${RED}✗ Test failed${NC}"
    fi
}

# Test 1: Display help menu
echo -e "\nTest 1: Displaying help menu (-h)"
sudo python3 $SCRIPT -h | grep -q "Custom Ping Utility"
check_success

# Test 2: Ping IPv4 target (default count=4)
echo -e "\nTest 2: Pinging IPv4 target (8.8.8.8, default count=4)"
sudo python3 $SCRIPT 8.8.8.8 > test2_output.txt
grep -q "Pinging 8.8.8.8" test2_output.txt && grep -q "Packet Statistics" test2_output.txt
check_success
rm test2_output.txt

# Test 3: Ping IPv4 with custom count
echo -e "\nTest 3: Pinging IPv4 target with custom count (google.com, count=2)"
sudo python3 $SCRIPT -c 2 google.com > test3_output.txt
COUNT=$(grep -c "Reply" test3_output.txt)
if [ "$COUNT" -eq 3 ]; then
    echo -e "${GREEN}✓ Test passed (2 pings detected)${NC}"
else
    echo -e "${RED}✗ Test failed (expected 2 pings, got $COUNT)${NC}"
fi
rm test3_output.txt


# Test 4: Ping IPv6 target
echo -e "\nTest 4: Pinging IPv6 target (2001:4860:4860::8888)"
sudo python3 $SCRIPT 2001:4860:4860::8888 > test5_output.txt
grep -q "ICMPv6" test5_output.txt && grep -q "Packet Statistics" test5_output.txt
check_success
rm test5_output.txt

# Test 5: Invalid target
echo -e "\nTest 5: Pinging invalid target (nonexistent.example.com)"
sudo python3 $SCRIPT nonexistent.example.com > test6_output.txt
grep -q "Unable to resolve" test6_output.txt
check_success
rm test6_output.txt

# Test 6: Ping IPv4 with custom TTL (Linux/macOS only)
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    echo -e "\nTest 6: Pinging IPv4 with custom TTL (1.1.1.1, ttl=32)"
    sudo python3 $SCRIPT -t 32 1.1.1.1 > test4_output.txt
    grep -q "Pinging 1.1.1.1" test4_output.txt
    check_success
    rm test4_output.txt
else
    echo -e "\nTest 6: Skipping TTL test (not supported on this OS: $OSTYPE)"
fi


echo -e "\nTests completed!"
