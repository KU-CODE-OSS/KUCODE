import axios from 'axios';

const ip_for_develop = 'http://61.72.142.8:10004/api'
// Axios 인스턴스 생성
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

export function getCourseTotalInfo() {
  return ajax(ip_for_develop + '/account/student_read_total', 'get')
}

export function postCourseUpload(formData) {
  return ajax(ip_for_develop + '/account/student_excel_import', 'post', { data: formData, headers })
}

export function getRepoInfo() {
  return ajax(ip_for_develop + '/repo/repo_read_db', 'get')
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