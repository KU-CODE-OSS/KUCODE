<template>
    <v-app>
      <v-container class="login-background" fluid>
        <v-row align="center" justify="center">
          <v-col cols="12" sm="8" md="4">
            <v-card class="elevation-12">
              <v-toolbar color="#78002f" dark flat>
                <v-toolbar-title>Login</v-toolbar-title>
              </v-toolbar>
              <v-card-text>
                <v-form>
                  <v-text-field
                    label="Username"
                    name="username"
                    prepend-icon="mdi-account"
                    type="text"
                  ></v-text-field>
                  <v-text-field
                    label="Password"
                    name="password"
                    prepend-icon="mdi-lock"
                    type="password"
                  ></v-text-field>
                </v-form>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="#78002f" text @click="login">Login</v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-app>
  </template>
  
  <script>
    export default {
      methods: {
        login() {
          console.log('로그인 시도')
        },
      },
    }
  </script>
  
  <style>
    .login-background {
      background-image: url('https://www.korea.ac.kr/mbshome/mbs/university/images/img/img_1_4_3_1_01.svg');
      background-size: auto; /* 이미지를 원본 크기로 유지 */
      background-position: center center; /* 이미지를 컨테이너의 중앙에 위치 */
      background-repeat: no-repeat; /* 이미지 반복 없음 */
      min-height: 100vh; /* 최소 높이를 화면 높이만큼 설정하여 전체 화면을 채움 */
      display: flex;
      align-items: center; /* 세로 방향 중앙 정렬 */
      justify-content: center; /* 가로 방향 중앙 정렬 */
    }
  </style>
  