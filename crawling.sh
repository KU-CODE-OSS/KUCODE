#!/bin/bash

# Define colors for success and failure
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# .env 파일에서 환경 변수 로드
if [ -f ".env" ]; then
    export $(cat .env | xargs)
else
    echo ".env file not found! Make sure it exists in the same directory."
    exit 1
fi

# Define the URLs for student synchronization
student_urls=(
    "$STUDENT_SYNC_URL"
)

# Define the URLs for repo synchronization
repo_urls=(
    "$REPO_SYNC_URL"
)

# Define the URLs for repo-related synchronization
repo_commit_urls=(
    "$REPO_COMMIT_SYNC_URL"
)

repo_issue_pr_urls=(
    "$REPO_ISSUE_SYNC_URL"
    "$REPO_PR_SYNC_URL"
)

repo_contributor_urls=(
    "$REPO_CONTRIBUTOR_SYNC_URL"
)

# Define the URLs to be processed for course-related operations
course_related_urls=(
    "$COURSE_OS_SYNC_URL"
    "$COURSE_CAPSTONE_SYNC_URL_1"
    "$COURSE_CLOUD_SYNC_URL"
    "$COURSE_SW_PROJECT_SYNC_URL"
    "$COURSE_CAPSTONE_SYNC_URL_2"
)

# Check if the script is already running
if [[ $(pgrep -f $(basename "$0") | wc -l) -gt 2 ]]; then
    echo "Script is already running."
    exit 1
fi

# Function to print a section header in the log
log_section() {
    local section_name=$1
    echo "## $section_name"
}

# Function to process each URL and log the result
process_url() {
    local url=$1
    local job_name=$2

    start_time=$(date +%Y-%m-%d\ %H:%M:%S)
    echo "## $job_name"
    echo "Starting: $start_time"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    curl_error_code=$?
    
    end_time=$(date +%Y-%m-%d\ %H:%M:%S)

    if [ "$response" -eq 200 ]; then
        echo -e "${GREEN}SUCCESS: Operation completed successfully.${NC}"
    else
        if [ "$curl_error_code" -ne 0 ]; then
            echo -e "${RED}FAILED: curl error (code: $curl_error_code)${NC}"
        else
            echo -e "${RED}FAILED: HTTP response code $response${NC}"
        fi
    fi
    echo "Ended: $end_time"
    echo "---------------------"
}

# Function to process URLs sequentially
process_urls_sequentially() {
    local urls=("$@")
    local job_name=$2
    for url in "${urls[@]}"; do
        process_url "$url" "$job_name"
    done
}

cycle_count=0

while true; do
    # Process student URLs first (student, repository, commit are in one cycle without empty lines)
    log_section "Student Synchronization"
    process_urls_sequentially "${student_urls[@]}" "Student Synchronization"

    log_section "Repo Synchronization"
    process_urls_sequentially "${repo_urls[@]}" "Repo Synchronization"

    log_section "Repo Commit Synchronization"
    process_urls_sequentially "${repo_commit_urls[@]}" "Repo Commit Synchronization"

    # Process course-related URLs
    log_section "Course Synchronization"
    process_urls_sequentially "${course_related_urls[@]}" "Course Synchronization"

    # 휴식 1시간 (로그에 표시되지 않음)
    sleep 1h

    # Process repo issue, PR, and contributor URLs sequentially in one cycle
    log_section "Repo Issue, PR, and Contributor Synchronization"
    process_urls_sequentially "${repo_issue_pr_urls[0]}" "Repo Issue Synchronization"
    process_urls_sequentially "${repo_issue_pr_urls[1]}" "Repo PR Synchronization"
    process_urls_sequentially "${repo_contributor_urls[@]}" "Repo Contributor Synchronization"

    # 휴식 1시간 (로그에 표시되지 않음)
    sleep 1h

    cycle_count=$((cycle_count + 1))
done
