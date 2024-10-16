#!/bin/bash

# Define the URLs for student synchronization
student_urls=(
    "http://localhost:8000/api/account/sync_student_db"
)

# Define the URLs for repo synchronization
repo_urls=(
    "http://localhost:8000/api/repo/sync_repo_db"
)

# Define the URLs to be processed in parallel for repo-related synchronization
repo_commit_urls=(
    "http://localhost:8000/api/repo/sync_repo_commit_db"
)

repo_issue_pr_urls=(
    "http://localhost:8000/api/repo/sync_repo_issue_db"
    "http://localhost:8000/api/repo/sync_repo_pr_db"
)

repo_contributor_urls=(
    "http://localhost:8000/api/repo/sync_repo_contributor_db"
)

# Define the URLs to be processed for course-related operations
course_related_urls=(
    # OS 
    "http://localhost:8000/api/course/course_project_update?course_id=COSE341-01&year=2024&semester=1"
    # 산악 캡스톤
    "http://localhost:8000/api/course/course_project_update?course_id=COSE480-00&year=2024&semester=1"
)

# File to store failed URLs
failed_urls_file="/tmp/failed_urls.txt"

# Check if the script is already running
if [[ $(pgrep -f $(basename "$0") | wc -l) -gt 2 ]]; then
    echo "Script is already running."
    exit 1
fi

# Function to process each URL
process_url() {
    local url=$1
    start_time=$(date +%s)
    response=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$url")
    end_time=$(date +%s)
    elapsed_time=$((end_time - start_time))
    
    # Convert elapsed time to hours, minutes, and seconds
    hours=$((elapsed_time / 3600))
    minutes=$(( (elapsed_time % 3600) / 60 ))
    seconds=$((elapsed_time % 60))
    
    if [ "$response" -eq 200 ]; then
        echo "Success: $url (Time taken: ${hours}h ${minutes}m ${seconds}s)"
    else
        echo "Failed: $url with response code $response (Time taken: ${hours}h ${minutes}m ${seconds}s)"
        echo "$url" >> "$failed_urls_file"
    fi
}

# Function to process URLs sequentially
process_urls_sequentially() {
    local urls=("$@")
    for url in "${urls[@]}"; do
        process_url "$url"
    done
}

# Function to process URLs in parallel with job control
process_urls_in_parallel() {
    local urls=("$@")
    local max_jobs=4
    local job_count=0
    
    for url in "${urls[@]}"; do
        ((job_count=job_count%max_jobs)); ((job_count++==0)) && wait
        process_url "$url" &
    done
    
    wait
}

# Function to process failed URLs
process_failed_urls() {
    if [ -f "$failed_urls_file" ]; then
        local failed_urls=()
        while IFS= read -r url; do
            failed_urls+=("$url")
        done < "$failed_urls_file"
        
        if [ ${#failed_urls[@]} -gt 0 ]; then
            echo "Retrying failed URLs from previous cycle..."
            process_urls_sequentially "${failed_urls[@]}"
            # Clear the file after processing
            : > "$failed_urls_file"
        fi
    fi
}

# Function to sleep until a specific time
sleep_until() {
    target_hour=$1
    target_minute=$2
    current_time=$(date +%s)
    target_time=$(date -d "today ${target_hour}:${target_minute}" +%s)
    sleep_seconds=$(( target_time - current_time ))
    if [ $sleep_seconds -lt 0 ]; then
        target_time=$(date -d "tomorrow ${target_hour}:${target_minute}" +%s)
        sleep_seconds=$(( target_time - current_time ))
    fi
    echo "All requests completed. Waiting until ${target_hour}:${target_minute} before the next cycle."
    sleep $sleep_seconds
}

cycle_count=0

while true; do
    start_time=$(date +"%Y-%m-%d %H:%M:%S")
    echo "Cycle started at: $start_time"

    # Process student URLs first in every cycle
    process_urls_sequentially "${student_urls[@]}"

    # Process failed URLs from the previous cycle
    process_failed_urls

    # Process repo URLs every 6 hours
    if (( cycle_count % 6 == 0 )); then
        process_urls_sequentially "${repo_urls[@]}"
    fi

    # Process course-related URLs every 6 hours
    if (( cycle_count % 6 == 0 )); then
        process_urls_sequentially "${course_related_urls[@]}"
    fi

    # Process repo commit URLs every 4 hours
    if (( cycle_count % 4 == 0 )); then
        process_urls_in_parallel "${repo_commit_urls[@]}"
    fi

    # Process repo issue and PR URLs every 3 hours
    if (( cycle_count % 3 == 0 )); then
        process_urls_in_parallel "${repo_issue_pr_urls[@]}"
    fi

    # Process repo contributor URLs every 6 hours
    if (( cycle_count % 6 == 0 )); then
        process_urls_in_parallel "${repo_contributor_urls[@]}"
    fi

    end_time=$(date +"%Y-%m-%d %H:%M:%S")
    echo "Cycle ended at: $end_time"

    echo "All requests completed. Waiting for 1 hour before the next cycle."
    sleep 1h

    cycle_count=$((cycle_count + 1))
done
