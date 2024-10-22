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
    # 산학 캡스톤 (1)
    "http://localhost:8000/api/course/course_project_update?course_id=COSE480-00&year=2024&semester=1"
    # 클라우드 컴퓨팅 (2)
    "http://localhost:8000/api/course/course_project_update?course_id=COSE444-00&year=2024&semester=2"
    # 실전 SW 프로젝트 (2)
    "http://localhost:8000/api/course/course_project_update?course_id=COSE457-00&year=2024&semester=2"
    # 산학 캡스톤 (2)
    "http://localhost:8000/api/course/course_project_update?course_id=COSE480-02&year=2024&semester=2"
)

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
    curl_exit_code=$?
    end_time=$(date +%s)
    elapsed_time=$((end_time - start_time))
    
    # Convert elapsed time to hours, minutes, and seconds
    hours=$((elapsed_time / 3600))
    minutes=$(( (elapsed_time % 3600) / 60 ))
    seconds=$((elapsed_time % 60))

    # Check if curl failed due to network issues
    if [ $curl_exit_code -ne 0 ]; then
        echo "Failed: $url with curl exit code $curl_exit_code (Time taken: ${hours}h ${minutes}m ${seconds}s)"
    elif [ "$response" -eq 200 ]; then
        echo "Success: $url (Time taken: ${hours}h ${minutes}m ${seconds}s)"
    else
        echo "Failed: $url with response code $response (Time taken: ${hours}h ${minutes}m ${seconds}s)"
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

cycle_count=0

while true; do
    start_time=$(date +"%Y-%m-%d %H:%M:%S")
    echo "Cycle started at: $start_time"

    # Process student URLs first
    process_urls_sequentially "${student_urls[@]}"

    # Process repo URLs next
    process_urls_sequentially "${repo_urls[@]}"

    # Process course-related URLs
    process_urls_sequentially "${course_related_urls[@]}"

    # Process repo issue, PR, and contributor URLs in parallel
    process_urls_in_parallel "${repo_issue_pr_urls[@]}" "${repo_contributor_urls[@]}"

    # Process repo commit URLs after parallel operations
    process_urls_sequentially "${repo_commit_urls[@]}"

    end_time=$(date +"%Y-%m-%d %H:%M:%S")
    echo "Cycle ended at: $end_time"

    echo "All requests completed. Waiting for 1 hour before the next cycle."
    sleep 1h

    cycle_count=$((cycle_count + 1))
done
