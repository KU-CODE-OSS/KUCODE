#!/bin/bash

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

# Define the URLs to be processed in parallel for repo-related synchronization
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
    echo ""
    echo "###########################################################"
    echo "## $section_name"
    echo "###########################################################"
}

# Function to process each URL and log the result
process_url() {
    local url=$1
    start_time=$(date +%Y-%m-%d\ %H:%M:%S)
    response=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$url")
    end_time=$(date +%Y-%m-%d\ %H:%M:%S)

    if [ "$response" -eq 200 ]; then
        echo "[$start_time] - SUCCESS: $url"
    else
        echo "[$start_time] - FAILED: $url (Response code: $response)"
    fi
    echo "Finished at: $end_time"
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
    echo ""
    echo "==========================================================="
    echo "Cycle started at: $start_time"
    echo "==========================================================="

    # Process student URLs first
    log_section "Student Synchronization"
    process_urls_sequentially "${student_urls[@]}"

    # Process repo URLs next
    log_section "Repo Synchronization"
    process_urls_sequentially "${repo_urls[@]}"

    # Process course-related URLs
    log_section "Course Synchronization"
    process_urls_sequentially "${course_related_urls[@]}"

    # 휴식 1시간 (로그에 표시되지 않음)
    sleep 1h

    # Process repo issue, PR, and contributor URLs in parallel
    log_section "Repo Issue, PR, and Contributor Synchronization (Parallel)"
    process_urls_in_parallel "${repo_issue_pr_urls[@]}" "${repo_contributor_urls[@]}"

    # 휴식 1시간 (로그에 표시되지 않음)
    sleep 1h

    # Process repo commit URLs after parallel operations
    log_section "Repo Commit Synchronization"
    process_urls_sequentially "${repo_commit_urls[@]}"

    end_time=$(date +"%Y-%m-%d %H:%M:%S")
    echo ""
    echo "==========================================================="
    echo "Cycle ended at: $end_time"
    echo "==========================================================="

    cycle_count=$((cycle_count + 1))
done
