# Node.js 18 Alpine 이미지 사용
FROM node:18-alpine

# 작업 디렉토리 설정
WORKDIR /app

# 환경변수 설정
ENV VUE_APP_API_URL=http://121.128.249.35:8000/api

# package.json과 package-lock.json 복사
COPY package*.json ./

# 의존성 설치
RUN npm install

# 소스 코드 복사
COPY . .

# 개발 서버 포트 노출
EXPOSE 5173

# 개발 서버 실행
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
