#!/bin/bash

# Class variables
WEBSITE_SOURCE_FILE="website.csv"
timeout=2

# Function to extract IPv4 and IPv6 addresses
get_ipv4_ipv6() {
    local website=$1

    # nslookup to get IPv4 and IPv6 addresses
    nslookup_ipv4=$(nslookup -type=A "$website" 2>/dev/null)
    nslookup_ipv6=$(nslookup -type=AAAA "$website" 2>/dev/null)

    # Extract IPs using regex
    ipv4=$(echo "$nslookup_ipv4" | grep -oE 'Address: [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | awk '{print $2}')
    ipv6=$(echo "$nslookup_ipv6" | grep -oE 'AAAA address\s+[0-9a-fA-F:]+' | awk '{print $3}')

    if [[ -z "$ipv4" || -z "$ipv6" ]]; then
        echo ""
    else
        echo "$ipv4 $ipv6"
    fi
}

# Function to get ping stats
get_ping_stats() {
    local ip_addr=$1
    local flag=$2

    sleep "1"
    if [[ "$flag" -eq 0 ]]; then
        ping_stats=$(ping -c 5 "$ip_addr" 2>/dev/null)
        min_rtt=$(echo "$ping_stats" | grep -oE 'min/avg/max/[a-z]+ = [0-9.]+/[0-9.]+/[0-9.]+/[0-9.]+' | awk -F= '{print $2}')
    else
        ping_stats=$(ping6 -c 5 "$ip_addr" 2>/dev/null)
        min_rtt=$(echo "$ping_stats" | grep -oE 'min/avg/max/std-dev = [0-9.]+/[0-9.]+/[0-9.]+/[0-9.]+' | awk -F= '{print $2}')
    fi

    if [[ -z "$min_rtt" ]]; then
        echo ""
    else
        echo "$min_rtt"
    fi
}

# Function to read websites from file
get_website_names() {
    cat "$WEBSITE_SOURCE_FILE"
}

# Function to save data to a file
save_data() {
    local data="$1"
    echo "$data" >> pingDataBash2.txt
}

# Main function to perform the test
main_test() {
    local stats_for_all_sites=""
    local website_addrs=$(get_website_names)

    while read -r website; do
        echo "Getting data for $website"
        
        ip_addrs=$(get_ipv4_ipv6 "$website")
        if [[ -z "$ip_addrs" ]]; then
            echo "IP addresses not found for $website"
            continue
        fi

        ipv4=$(echo "$ip_addrs" | awk '{print $1}')
        ipv6=$(echo "$ip_addrs" | awk '{print $2}')

        ipv4_ping_stats=$(get_ping_stats "$ipv4" 0)
        ipv6_ping_stats=$(get_ping_stats "$ipv6" 1)


        if [[ -z "$ipv4_ping_stats" || -z "$ipv6_ping_stats" ]]; then
            echo "Ping stats not found for $website"
            continue
        fi

        complete_data="$website, $ipv4, $ipv4_ping_stats, $ipv6, $ipv6_ping_stats"
        stats_for_all_sites+="$complete_data"$'\n'
        
        echo "Data for $website"
        echo "IPv4: $ipv4: $ipv4_ping_stats"
        echo "IPv6: $ipv6: $ipv6_ping_stats"

    done <<< "$website_addrs"

    save_data "$stats_for_all_sites"
}

# Run the main test function
main_test

