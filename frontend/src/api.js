import axios from 'axios';

// Vite 환경 변수 사용 + 기본값 '/api'
const API_BASE_URL = import.meta.env.VITE_API_BASE || '/api';

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: API_BASE_URL,
  xsrfHeaderName: 'X-CSRFToken',
  xsrfCookieName: 'csrftoken'
});

const headers = {
  'Content-Type': 'multipart/form-data'
};

// 전역 에러 핸들링 함수
function handleError(error) {
  console.error("API Error:", error.response?.data || error);
  // 필요하면 여기서 공통 처리
}

// 공통 ajax 함수
function ajax(url, method, { params = {}, data = {}, headers = {} } = {}) {
  return new Promise((resolve, reject) => {
    api({ url, method, params, data, headers })
      .then(response => {
        if (response.data?.error) {
          reject(new Error(response.data.data));
        } else {
          resolve(response);
        }
      })
      .catch(error => {
        handleError(error);
        reject(error);
      });
  });
}

/* ====== 여기서부터는 전부 "상대 경로"만 사용 ====== */

// Health Check
export function getHealthCheck() {
  // DRF 문서가 /api/healthcheck 라고 되어 있으니
  // baseURL = /api, url = /healthcheck → 최종 /api/healthcheck
  return ajax('/healthcheck', 'get');
}

// Course 관련
export function getCourseInfo() {
  return ajax('/account/student_read_course_info', 'get');
}

export function getCourseReadMinMaxAvg() {
  return ajax('/course/course_read_min_max_avg', 'get');
}

export function getCourseReadDB() {
  return ajax('/course/course_read_db', 'get');
}

export function getCourseTotalInfo() {
  return ajax('/account/student_read_total', 'get');
}

export function getCourseStudentInfo() {
  return ajax('/course/course_department_count', 'get');
}

export function postCourseUpload(formData) {
  return ajax('/account/student_excel_import', 'post', { data: formData, headers });
}

// Repo 관련
export function getRepoInfo() {
  return ajax('/repo/repo_read_db', 'get');
}

// 히트맵 API
export function getEProfileHeatmap(student_uuid) {
  const data = { uuid: student_uuid };

  return ajax('/repo/repo_account_read_db', 'post', {
    data,
    headers: { 'Content-Type': 'application/json' }
  });
}

// Authentication / Login 등
export function checkStudentIdNumber(student_id, student_name) {
  return ajax('/authentication/studentIdNumber_verification', 'get', {
    params: { student_id, student_name }
  });
}

export function createSignUp(signup_data) {
  return ajax('/login/signup', 'post', { data: signup_data });
}

export function updateStudentIntroduction(uuid, introduction) {
  return ajax('/account/update_student_introduction', 'post', {
    data: { uuid, introduction },
    headers: { 'Content-Type': 'application/json' }
  });
}

export function updateStudentTechnologyStack(uuid, technology_stack) {
  return ajax('/account/update_student_technology_stack', 'post', {
    data: { uuid, technology_stack },
    headers: { 'Content-Type': 'application/json' }
  });
}

export function updateRepoIntroduction(uuid, repo_id, project_introduction) {
  return ajax('/repo/update_repo_introduction', 'post', {
    data: { uuid, repo_id, project_introduction },
    headers: { 'Content-Type': 'application/json' }
  });
}

// Board Posts APIs
export function getBoardPostsList(page = 1, size = 10, uuid) {
  return ajax('/board/read_posts_list', 'get', {
    params: { page, count: size, uuid }
  });
}

export function getBoardPost(postId) {
  return ajax('/board/read_post', 'get', {
    params: { post_id: postId }
  });
}

// Company Repos APIs
export function getCompanyReposList(page = 1, size = 10) {
  return ajax('/board/read_company_repos_list', 'get', {
    params: { page, count: size }
  });
}

// Trending Repos APIs
export function getTrendingReposList(page = 1, size = 10) {
  return ajax('/board/read_trending_repos_list', 'get', {
    params: { page, count: size }
  });
}

// Create/Update Post
export function createOrUpdatePost(postData) {
  return ajax('/board/update_post', 'post', {
    data: postData,
    headers: { 'Content-Type': 'application/json' }
  });
}

// Create/Update Company Repo
export function createOrUpdateCompanyRepo(repoData) {
  return ajax('/board/update_company_repo', 'post', {
    data: repoData,
    headers: { 'Content-Type': 'application/json' }
  });
}

// Create/Update Trending Repo
export function createOrUpdateTrendingRepo(repoData) {
  return ajax('/board/update_trending_repo', 'post', {
    data: repoData,
    headers: { 'Content-Type': 'application/json' }
  });
}

// Google Drive Configuration
export function getDriveConfig() {
  return ajax('/board/drive_config', 'get');
}

// Upload File to Google Drive
export function uploadFileToDrive(postId, file, displayType = 'DOWNLOAD') {
  const formData = new FormData();
  formData.append('post_id', postId);
  formData.append('file', file);
  formData.append('display_type', displayType);

  return ajax('/board/upload_file_to_drive', 'post', {
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  });
}

// Link Google Drive File
export function linkDriveFile(postId, driveUrl, fileName = null, displayType = 'DOWNLOAD') {
  return ajax('/board/link_drive_file', 'post', {
    data: {
      post_id: postId,
      drive_url: driveUrl,
      file_name: fileName,
      display_type: displayType
    },
    headers: { 'Content-Type': 'application/json' }
  });
}

// Login Role API
export function postLoginRole(uuid) {
  return ajax('/login/signin', 'post', {
    data: { uuid },
    headers: { 'Content-Type': 'application/json' }
  });
}

// PDF Export API
export function exportProfilePdf(uuid, repoIds) {
  return ajax('/repo/export_profile_pdf', 'post', {
    data: { uuid, repo_ids: repoIds },
    headers: { 'Content-Type': 'application/json' }
  });
}

// Likes & Comments APIs
export function togglePostLike(postId, memberId) {
  return ajax('/board/toggle_post_like', 'post', {
    data: { post_id: postId, member_id: memberId },
    headers: { 'Content-Type': 'application/json' }
  });
}

export function addComment(postId, authorId, content, parentId = null) {
  return ajax('/board/add_comment', 'post', {
    data: { post_id: postId, author_id: authorId, content, parent_id: parentId },
    headers: { 'Content-Type': 'application/json' }
  });
}

export function deleteComment(commentId, authorId) {
  return ajax('/board/delete_comment', 'post', {
    data: { comment_id: commentId, author_id: authorId },
    headers: { 'Content-Type': 'application/json' }
  });
}

export function getComments(postId, page = 1, size = 10) {
  return ajax('/board/read_comments_list', 'get', {
    params: { post_id: postId, page, count: size }
  });
}
