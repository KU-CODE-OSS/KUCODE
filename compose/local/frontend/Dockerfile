FROM node:18.20.4-slim

WORKDIR /app

COPY ./frontend/package*.json ./

RUN npm install

COPY ./frontend .

ENV PATH=/app/node_modules/.bin:$PATH

EXPOSE 8080