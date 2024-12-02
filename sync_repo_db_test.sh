#!/bin/bash

# Define colors for success and failure, apply only in interactive terminal
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    NC='\033[0m'
else
    GREEN=''
    RED=''
    NC=''
fi

# Load environment variables from .env file
if [ -f ".env" ]; then
    source .env
else
    echo ".env file not found! Make sure it exists in the same directory."
    exit 1
fi

# Define URLs for student synchronization task
student_urls=("$STUDENT_SYNC_URL")

# Function to log a section header
log_section() {
    echo "## $1"
}

# Function to process each URL and log the result
process_url() {
    local url=$1
    echo "Processing URL: $url"
    local start_time=$(date +%Y-%m-%d\ %H:%M:%S)
    echo "Starting: $start_time"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    local end_time=$(date +%Y-%m-%d\ %H:%M:%S)

    if [ "$response" -eq 200 ]; then
        echo -e "${GREEN}SUCCESS: Operation completed successfully.${NC}"
    else
        echo -e "${RED}FAILED: HTTP response code $response${NC} (URL: $url)"
    fi
    echo "Ended: $end_time"
    echo "---------------------"
}

# Function to process multiple URLs sequentially with a section log
process_urls_sequentially() {
    local -n urls=$1
    local job_name=$2
    log_section "$job_name"
    for url in "${urls[@]}"; do
        if [ -n "$url" ]; then
            process_url "$url"
        fi
    done
}

# Main execution: Test Student Synchronization only
process_urls_sequentially student_urls "Student Synchronization Test"
