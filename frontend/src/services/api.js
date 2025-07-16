import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

// Create axios instance with credentials
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Response interceptor to handle authentication errors
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Redirect to login if unauthorized
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// export const authAPI = {
//   login: (idToken) => api.post('/auth/login/', { idToken }),
//   logout: () => api.post('/auth/logout/'),
//   sessionStatus: () => api.get('/auth/session-status/'),
//   protected: () => api.get('/auth/protected/')
// }

export default api