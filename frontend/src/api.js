import axios from 'axios';

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL,
  xsrfHeaderName: 'X-CSRFToken',
  xsrfCookieName: 'csrftoken'
});

// 전역 에러 핸들링 함수
function handleError(error) {
  console.error("API Error:", error.response.data);
  // 오류에 따른 추가적인 액션을 취할 수 있습니다.
}

export function getHealthCheck() {
    return ajax('/account/healthcheck', 'get');
}

export function getCourseInfo() {
  return ajax('http://119.28.232.108:8000/api/account/student_read_course_info', 'get')
}
  
// ajax 함수
function ajax(url, method, { params = {}, data = {} } = {}) {
  return new Promise((resolve, reject) => {
    api({ url, method, params, data }).then(response => {
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