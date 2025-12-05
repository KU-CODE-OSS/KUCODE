import axios from 'axios';

const ip_for_develop = process.env.VUE_APP_API_URL;
// // Axios 인스턴스 생성
const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL,
  xsrfHeaderName: 'X-CSRFToken',
  xsrfCookieName: 'csrftoken'
});

const headers = {
  'Content-Type': 'multipart/form-data'
};

// 전역 에러 핸들링 함수
function handleError(error) {
  console.error("API Error:", error.response.data);
  // 오류에 따른 추가적인 액션을 취할 수 있습니다.
}

export function getHealthCheck() {
  return ajax('/account/healthcheck', 'get');
}

export function getCourseInfo() {
  return ajax(ip_for_develop + '/account/student_read_course_info', 'get')
}

export function getCourseReadMinMaxAvg() {
  return ajax(ip_for_develop + '/course/course_read_min_max_avg', 'get')
}


export function getCourseReadDB() {
  return ajax(ip_for_develop + '/course/course_read_db', 'get')
}

export function getCourseTotalInfo() {
  return ajax(ip_for_develop + '/account/student_read_total', 'get')
}

export function getCourseStudentInfo() {
  return ajax(ip_for_develop + '/course/course_department_count', 'get')
}

export function postCourseUpload(formData) {
  return ajax(ip_for_develop + '/account/student_excel_import', 'post', { data: formData, headers })
}

export function getRepoInfo() {
  return ajax(ip_for_develop + '/repo/repo_read_db', 'get')
}

// 히트맵 API 함수 (POST 방식)
export function getEProfileHeatmap(student_uuid, student_num) {
  // 전송할 데이터를 JSON 객체로 만듭니다.
  const data = {
    uuid: student_uuid,
    student_num: student_num
  };

  // ajax 함수 호출 시 'data' 인자로 JSON 객체를 전달합니다.
  // 'Content-Type': 'application/json' 헤더를 추가해야 백엔드에서 JSON으로 인식합니다.
  return ajax(ip_for_develop + '/repo/repo_account_read_db', 'post', { 
    data: data, 
    headers: { 'Content-Type': 'application/json' } 
  });
}

// ajax 함수
function ajax(url, method, { params = {}, data = {}, headers = {} } = {}) {
  return new Promise((resolve, reject) => {
    api({ url, method, params, data, headers }).then(response => {
      if (response.data.error) {
        reject(new Error(response.data.data));
      } else {
        resolve(response);
      }
    }).catch(error => {
      reject(error);
    });
  });
}

export function checkStudentIdNumber(student_id, student_name) {
  return ajax(ip_for_develop + '/authentication/studentIdNumber_verification', 'get', {params: {student_id: student_id, student_name: student_name}})
}

export function createSignUp(signup_data) {
  return ajax(ip_for_develop + '/login/signup', 'post', {
    data: signup_data
  })
}

export function updateStudentIntroduction(uuid, introduction) {  
  return ajax(ip_for_develop + '/account/update_student_introduction', 'post', {
    data: { uuid, introduction },
    headers: { 'Content-Type': 'application/json' }
  })
}

export function updateStudentTechnologyStack(uuid, technology_stack) {
  return ajax(ip_for_develop + '/account/update_student_technology_stack', 'post', {
    data: { uuid, technology_stack },
    headers: { 'Content-Type': 'application/json' }
  })
}

export function updateRepoIntroduction(uuid, repo_id, project_introduction) {
  return ajax(ip_for_develop + '/repo/update_repo_introduction', 'post', {
    data: { uuid, repo_id, project_introduction },
    headers: { 'Content-Type': 'application/json' }
  })
}

// Board Posts APIs
export function getBoardPostsList(page = 1, size = 10, uuid) {
  return ajax(ip_for_develop + '/board/read_posts_list', 'get', {
    params: { page, count: size, uuid }
  })
}

export function getBoardPost(postId) {
  return ajax(ip_for_develop + '/board/read_post', 'get', {
    params: { post_id: postId }
  })
}

// Company Repos APIs
export function getCompanyReposList(page = 1, size = 10) {
  return ajax(ip_for_develop + '/board/read_company_repos_list', 'get', {
    params: { page, count: size }
  })
}

// Trending Repos APIs
export function getTrendingReposList(page = 1, size = 10) {
  return ajax(ip_for_develop + '/board/read_trending_repos_list', 'get', {
    params: { page, count: size }
  })
}

// Create/Update Post
export function createOrUpdatePost(postData) {
  return ajax(ip_for_develop + '/board/update_post', 'post', {
    data: postData,
    headers: { 'Content-Type': 'application/json' }
  })
}

// Create/Update Company Repo
export function createOrUpdateCompanyRepo(repoData) {
  return ajax(ip_for_develop + '/board/update_company_repo', 'post', {
    data: repoData,
    headers: { 'Content-Type': 'application/json' }
  })
}

// Create/Update Trending Repo
export function createOrUpdateTrendingRepo(repoData) {
  return ajax(ip_for_develop + '/board/update_trending_repo', 'post', {
    data: repoData,
    headers: { 'Content-Type': 'application/json' }
  })
}

// Google Drive Configuration
export function getDriveConfig() {
  return ajax(ip_for_develop + '/board/drive_config', 'get')
}

// Upload File to Google Drive
export function uploadFileToDrive(postId, file, displayType = 'DOWNLOAD') {
  const formData = new FormData()
  formData.append('post_id', postId)
  formData.append('file', file)
  formData.append('display_type', displayType)

  return ajax(ip_for_develop + '/board/upload_file_to_drive', 'post', {
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// Link Google Drive File
export function linkDriveFile(postId, driveUrl, fileName = null, displayType = 'DOWNLOAD') {
  return ajax(ip_for_develop + '/board/link_drive_file', 'post', {
    data: {
      post_id: postId,
      drive_url: driveUrl,
      file_name: fileName,
      display_type: displayType
    },
    headers: { 'Content-Type': 'application/json' }
  })
}

// Login Role API
export function postLoginRole(uuid) {
  return ajax(ip_for_develop + '/login/signin', 'post', {
    data: { uuid },
    headers: { 'Content-Type': 'application/json' }
  })
}

// PDF Export API (Placeholder - to be replaced with backend implementation)
export function exportProfilePdf(uuid, repoIds) {
  // TODO: PLACEHOLDER_API_CALL - This will be replaced with actual backend PDF generation
  return ajax(ip_for_develop + '/repo/export_profile_pdf', 'post', {
    data: { uuid, repo_ids: repoIds },
    headers: { 'Content-Type': 'application/json' }
  })
}

// Likes & Comments APIs
export function togglePostLike(postId, memberId) {
  return ajax(ip_for_develop + '/board/toggle_post_like', 'post', {
    data: { post_id: postId, member_id: memberId },
    headers: { 'Content-Type': 'application/json' }
  })
}

export function addComment(postId, authorId, content, parentId = null) {
  return ajax(ip_for_develop + '/board/add_comment', 'post', {
    data: { post_id: postId, author_id: authorId, content, parent_id: parentId },
    headers: { 'Content-Type': 'application/json' }
  })
}

export function deleteComment(commentId, authorId) {
  return ajax(ip_for_develop + '/board/delete_comment', 'post', {
    data: { comment_id: commentId, author_id: authorId },
    headers: { 'Content-Type': 'application/json' }
  })
}

export function getComments(postId, page = 1, size = 10) {
  return ajax(ip_for_develop + '/board/read_comments_list', 'get', {
    params: { post_id: postId, page, count: size }
  })
}