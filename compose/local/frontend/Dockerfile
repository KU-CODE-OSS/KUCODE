<<<<<<< HEAD
FROM node:20-slim

WORKDIR /app

COPY ./frontend/package*.json .
=======
FROM node:18.20.4-slim

WORKDIR /app

COPY ./frontend/package*.json ./
>>>>>>> e80889aa93fa1e2571004a53d18083cb267d2514

RUN npm install

COPY ./frontend .

ENV PATH=/app/node_modules/.bin:$PATH

EXPOSE 8080