import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'

const firebaseConfig = {
  apiKey: "AIzaSyAGWYWMg1E6pPNTfZOTTx-gxF-huJXtoc8",
  authDomain: "kuoss-c21a5.firebaseapp.com",
  projectId: "kuoss-c21a5",
  storageBucket: "kuoss-c21a5.firebasestorage.app",
  messagingSenderId: "122365668734",
  appId: "1:122365668734:web:81d9ff8025691b6186972f",
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app)
export default app