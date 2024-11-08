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

# Define URLs for synchronization tasks
student_urls=("$STUDENT_SYNC_URL")
repo_urls=("$REPO_SYNC_URL")
repo_commit_urls=("$REPO_COMMIT_SYNC_URL")
course_related_urls=(
    "$COURSE_20241OS01_SYNC_URL" "$COURSE_20241CAPSTONE00_SYNC_URL"
    "$COURSE_20242CLOUD00_SYNC_URL" "$COURSE_20242SWPROJECT00_SYNC_URL"
    "$COURSE_20242CAPSTONE02_SYNC_URL" "$COURSE_20242SWENGINEERING00_SYNC_URL"
    "$COURSE_20242DL02_SYNC_URL" "$COURSE_20242CAPSTONE01_SYNC_URL"
)
repo_issue_url="$REPO_ISSUE_SYNC_URL"
repo_pr_url="$REPO_PR_SYNC_URL"
repo_contributor_url="$REPO_CONTRIBUTOR_SYNC_URL"

# Check if the script is already running
if [[ $(pgrep -f $(basename "$0") | wc -l) -gt 2 ]]; then
    echo "Script is already running."
    exit 1
fi

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

# Run twice-daily tasks with a 1-hour delay in between
run_twice_daily_tasks() {
    for _ in {1..2}; do
        #process_urls_sequentially student_urls "Student Synchronization"

        process_urls_sequentially repo_urls "Repo Synchronization"
        process_urls_sequentially course_related_urls "Course Synchronization"
        sleep 1h
    done
}

# Run once-daily tasks sequentially with 1-hour delays in between
run_once_daily_tasks() {
    log_section "Repo Issue, PR, and Contributor Synchronization"
    process_url "$repo_issue_url"
    sleep 1h

    process_url "$repo_pr_url"
    sleep 1h

    process_url "$repo_contributor_url"
    sleep 1h
}

# Main loop
while true; do
    run_twice_daily_tasks
    run_once_daily_tasks

    # Continuously perform repo commit sync with a 1-hour delay
    while true; do
        process_urls_sequentially repo_commit_urls "Repo Commit Synchronization"
        sleep 1h
    done
done
