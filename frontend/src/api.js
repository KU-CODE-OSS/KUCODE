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
export function getEProfileHeatmap(student_uuid) {
  // 전송할 데이터를 JSON 객체로 만듭니다.
  const data = {
    uuid: student_uuid
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