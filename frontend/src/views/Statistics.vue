<template>
  <div class="default-container">
    <div class="left-split">
      <div class="empty-box"></div>
      <!-- 전체 Filter -->
      <div v-show="getRouteType() === 1" class="filter-box">
        <div class="filter-title-box">
          <div class="title">필터</div>
          <v-btn class="init" variant="outlined" v-on:click="resetFilterforStudent" color="#f5d6de">초기화</v-btn>
        </div>
        <div class="filter-container">
          <!-- year 필터 한 개 시작 -->
          <div class=types :class="[this.yearDropped ? 'types-focused' : 'types-unfocused']">
            <svg v-show="this.yearDropped" id="type-svg" xmlns="http://www.w3.org/2000/svg" width="24" height="24"
              viewBox="0 0 24 24" fill="none">
              <path
                d="M3 9V18C3 20.2091 4.79086 22 7 22H17C19.2091 22 21 20.2091 21 18V9M3 9V7.5C3 5.29086 4.79086 3.5 7 3.5H17C19.2091 3.5 21 5.29086 21 7.5V9M3 9H21M16 2V5M8 2V5"
                stroke="#910024" stroke-width="1.5" stroke-linecap="round" />
            </svg>
            <svg v-show="!this.yearDropped" id="type-svg" xmlns="http://www.w3.org/2000/svg" width="24" height="24"
              viewBox="0 0 24 24" fill="none">
              <path
                d="M3 9V18C3 20.2091 4.79086 22 7 22H17C19.2091 22 21 20.2091 21 18V9M3 9V7.5C3 5.29086 4.79086 3.5 7 3.5H17C19.2091 3.5 21 5.29086 21 7.5V9M3 9H21M16 2V5M8 2V5"
                stroke="#262626" stroke-width="1.5" stroke-linecap="round" />
            </svg>
            <p class="type-title">
              연도
            </p>
            <button class="drop-btn"><i class="drop-btn-container" v-on:click="yearbtnclick">
                <svg class="toggle-btn" v-show="this.yearDropped" xmlns="http://www.w3.org/2000/svg" width="12"
                  height="8" viewBox="0 0 12 8" fill="none">
                  <path d="M1 6.5L5.29289 2.20711C5.68342 1.81658 6.31658 1.81658 6.70711 2.20711L11 6.5"
                    stroke="#910024" stroke-width="2" stroke-linecap="round" />
                </svg>
                <svg class="toggle-btn" v-show="!this.yearDropped" xmlns="http://www.w3.org/2000/svg" width="13"
                  height="7" viewBox="0 0 13 7" fill="none">
                  <path d="M11.4521 1L7.15925 5.29289C6.76873 5.68342 6.13557 5.68342 5.74504 5.29289L1.45215 0.999999"
                    stroke="#CDCDCD" stroke-width="2" stroke-linecap="round" />
                </svg>
              </i></button>
          </div>
          <transition name="slide">
            <ul class="year-filter no-dot" v-if="yearDropped">
              <li class="item" v-for="(year, index) in studentFilterYearsCheckbox">
                <label :for="'year' + index + 'student'" class="checkbox-label">
                  <input :id="'year' + index + 'student'" type="checkbox" class="checkbox" :value="year"
                    v-model="selectedYearItemsforStudent" @change="yearFilterEventChangeforStudent(year, $event)">
                  <p v-if="year === '-1' || year === ''" class="label-text">기타</p>
                  <p v-else class="label-text">{{ year }}</p>
                </label>
              </li>
            </ul>
          </transition>
          <!-- year 필터 한 개 끝 -->

          <!-- 학기 필터 한 개 시작 -->
          <div class=types :class="[this.semesterDropped ? 'types-focused' : 'types-unfocused']">

            <svg v-show="this.semesterDropped" id="type-svg" xmlns="http://www.w3.org/2000/svg" width="24" height="25"
              viewBox="0 0 24 25" fill="none">
              <path
                d="M7.9405 9.5H11.9109M7.9405 13.5H15.8812M7.9405 17.5H15.8812M15.8808 2.5V5.5M7.94002 2.5V5.5M6.94791 4H16.8738C19.0666 4 20.8442 5.79086 20.8442 8V18.5C20.8442 20.7091 19.0666 22.5 16.8738 22.5H6.94791C4.75513 22.5 2.97754 20.7091 2.97754 18.5V8C2.97754 5.79086 4.75513 4 6.94791 4Z"
                stroke="#910024" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <svg v-show="!this.semesterDropped" id="type-svg" xmlns="http://www.w3.org/2000/svg" width="24" height="25"
              viewBox="0 0 24 25" fill="none">
              <path
                d="M7.9405 9.5H11.9109M7.9405 13.5H15.8812M7.9405 17.5H15.8812M15.8808 2.5V5.5M7.94002 2.5V5.5M6.94791 4H16.8738C19.0666 4 20.8442 5.79086 20.8442 8V18.5C20.8442 20.7091 19.0666 22.5 16.8738 22.5H6.94791C4.75513 22.5 2.97754 20.7091 2.97754 18.5V8C2.97754 5.79086 4.75513 4 6.94791 4Z"
                stroke="#262626" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <p class="type-title">
              학기
            </p>
            <button class="drop-btn"><i class="drop-btn-container" v-on:click="semesterbtnclick">
                <svg class="toggle-btn" v-show="this.semesterDropped" xmlns="http://www.w3.org/2000/svg" width="12"
                  height="8" viewBox="0 0 12 8" fill="none">
                  <path d="M1 6.5L5.29289 2.20711C5.68342 1.81658 6.31658 1.81658 6.70711 2.20711L11 6.5"
                    stroke="#910024" stroke-width="2" stroke-linecap="round" />
                </svg>
                <svg class="toggle-btn" v-show="!this.semesterDropped" xmlns="http://www.w3.org/2000/svg" width="13"
                  height="7" viewBox="0 0 13 7" fill="none">
                  <path d="M11.4521 1L7.15925 5.29289C6.76873 5.68342 6.13557 5.68342 5.74504 5.29289L1.45215 0.999999"
                    stroke="#CDCDCD" stroke-width="2" stroke-linecap="round" />
                </svg>
              </i></button>
          </div>
          <transition name="slide">
            <ul class="year-filter no-dot" v-if="semesterDropped">
              <li class="item" v-for="(semester, index) in studentFilterSemesterCheckbox" :key="index">
                <label :for="'semester' + index + 'student'" class="checkbox-label">
                  <input :id="'semester' + index + 'student'" type="checkbox" class="checkbox" :value="semester"
                    v-model="selectedSemesterItemsforStudent"
                    @change="semesterFilterEventChangeforStudent(semester, $event)">
                  <p v-if="semester === '-1' || semester === ''" class="label-text">기타</p>
                  <p v-else class="label-text">{{ semester }} 학기</p>
                </label>
              </li>
            </ul>
          </transition>
          <!-- 학기 필터 한 개 끝 -->

          <!-- 과목명 필터 한 개 시작 -->
          <div class=types :class="[this.coursenameDropped ? 'types-focused' : 'types-unfocused']">
            <svg id="type-svg" xmlns="http://www.w3.org/2000/svg" v-show="this.coursenameDropped" width="24" height="25"
              viewBox="0 0 24 25" fill="none">
              <path
                d="M12 6.55337V20.8025M5 8.75464C6.26578 8.95067 7.67778 9.27657 9 9.78788M5 12.7546C5.63949 12.8537 6.3163 12.9859 7 13.1584M3.99433 3.51127C6.21271 3.76195 9.19313 4.43632 11.3168 5.92445C11.725 6.21045 12.275 6.21045 12.6832 5.92445C14.8069 4.43632 17.7873 3.76195 20.0057 3.51127C21.1036 3.38721 22 4.30402 22 5.43518V16.7C22 17.8311 21.1036 18.7483 20.0057 18.8723C17.7873 19.123 14.8069 19.7974 12.6832 21.2855C12.275 21.5715 11.725 21.5715 11.3168 21.2855C9.19313 19.7974 6.21271 19.123 3.99433 18.8723C2.89642 18.7483 2 17.8311 2 16.7V5.43518C2 4.30402 2.89642 3.38721 3.99433 3.51127Z"
                stroke="#910024" stroke-width="1.5" stroke-linecap="round" />
            </svg>
            <svg id="type-svg" xmlns="http://www.w3.org/2000/svg" v-show="!this.coursenameDropped" width="24"
              height="25" viewBox="0 0 24 25" fill="none">
              <path
                d="M12 6.55337V20.8025M5 8.75464C6.26578 8.95067 7.67778 9.27657 9 9.78788M5 12.7546C5.63949 12.8537 6.3163 12.9859 7 13.1584M3.99433 3.51127C6.21271 3.76195 9.19313 4.43632 11.3168 5.92445C11.725 6.21045 12.275 6.21045 12.6832 5.92445C14.8069 4.43632 17.7873 3.76195 20.0057 3.51127C21.1036 3.38721 22 4.30402 22 5.43518V16.7C22 17.8311 21.1036 18.7483 20.0057 18.8723C17.7873 19.123 14.8069 19.7974 12.6832 21.2855C12.275 21.5715 11.725 21.5715 11.3168 21.2855C9.19313 19.7974 6.21271 19.123 3.99433 18.8723C2.89642 18.7483 2 17.8311 2 16.7V5.43518C2 4.30402 2.89642 3.38721 3.99433 3.51127Z"
                stroke="#262626" stroke-width="1.5" stroke-linecap="round" />
            </svg>
            <p class="type-title">
              과목
            </p>
            <button class="drop-btn"><i class="drop-btn-container" v-on:click="coursenamebtnclick">
                <svg class="toggle-btn" v-show="this.coursenameDropped" xmlns="http://www.w3.org/2000/svg" width="12"
                  height="8" viewBox="0 0 12 8" fill="none">
                  <path d="M1 6.5L5.29289 2.20711C5.68342 1.81658 6.31658 1.81658 6.70711 2.20711L11 6.5"
                    stroke="#910024" stroke-width="2" stroke-linecap="round" />
                </svg>
                <svg class="toggle-btn" v-show="!this.coursenameDropped" xmlns="http://www.w3.org/2000/svg" width="13"
                  height="7" viewBox="0 0 13 7" fill="none">
                  <path d="M11.4521 1L7.15925 5.29289C6.76873 5.68342 6.13557 5.68342 5.74504 5.29289L1.45215 0.999999"
                    stroke="#CDCDCD" stroke-width="2" stroke-linecap="round" />
                </svg>
              </i></button>
          </div>
          <transition name="slide">
            <ul class="year-filter no-dot" v-if="coursenameDropped">
              <li class="item" v-for="(course, index) in uniqueCourses" :key="index">
                <label :for="'course' + index + 'student'" class="checkbox-label">
                  <input :id="'course' + index + 'student'" type="checkbox" class="checkbox" :value="course.course_name"
                    v-model="selectedCourseNameItemsforStudent"
                    @change="courseNameFilterEventChangeforStudent(course, $event)">
                  <p v-if="course.course_name === '기타' || course.course_name === ''" class="label-text">기타</p>
                  <p v-else class="label-text">{{ course.course_name }}</p>
                </label>
              </li>
            </ul>
          </transition>
          <!-- 과목명 필터 한 개 끝 -->
          <!-- (학생 탭) 분반 필터 한 개 시작 -->
          <div class=types :class="[this.courseIdDropped ? 'types-focused' : 'types-unfocused']">

            <svg v-show="this.courseIdDropped" id="type-svg" xmlns="http://www.w3.org/2000/svg" width="24" height="25"
              viewBox="0 0 24 25" fill="none">
              <path
                d="M7 14s-1 0-1-1 1-4 5-4 5 3 5 4-1 1-1 1zm4-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6m-5.784 6A2.24 2.24 0 0 1 5 13c0-1.355.68-2.75 1.936-3.72A6.3 6.3 0 0 0 5 9c-4 0-5 3-5 4s1 1 1 1zM4.5 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5"
                stroke="#910024" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <svg v-show="!this.courseIdDropped" id="type-svg" xmlns="http://www.w3.org/2000/svg" width="24" height="25"
              viewBox="0 0 24 25" fill="none">
              <path
                d="M7 14s-1 0-1-1 1-4 5-4 5 3 5 4-1 1-1 1zm4-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6m-5.784 6A2.24 2.24 0 0 1 5 13c0-1.355.68-2.75 1.936-3.72A6.3 6.3 0 0 0 5 9c-4 0-5 3-5 4s1 1 1 1zM4.5 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5"
                stroke="#262626" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <p class="type-title">
              분반
            </p>
            <button class="drop-btn"><i class="drop-btn-container" v-on:click="courseIdbtnclick">
                <svg class="toggle-btn" v-show="this.courseIdDropped" xmlns="http://www.w3.org/2000/svg" width="12"
                  height="8" viewBox="0 0 12 8" fill="none">
                  <path d="M1 6.5L5.29289 2.20711C5.68342 1.81658 6.31658 1.81658 6.70711 2.20711L11 6.5"
                    stroke="#910024" stroke-width="2" stroke-linecap="round" />
                </svg>
                <svg class="toggle-btn" v-show="!this.courseIdDropped" xmlns="http://www.w3.org/2000/svg" width="13"
                  height="7" viewBox="0 0 13 7" fill="none">
                  <path d="M11.4521 1L7.15925 5.29289C6.76873 5.68342 6.13557 5.68342 5.74504 5.29289L1.45215 0.999999"
                    stroke="#CDCDCD" stroke-width="2" stroke-linecap="round" />
                </svg>
              </i></button>
          </div>
          <transition name="slide">
            <ul class="year-filter no-dot" v-if="courseIdDropped">
              <li class="item" v-for="(course_id, index) in uniqueCourseIDs" :key="index">
                <label :for="'course_id' + index" class="checkbox-label">
                  <input :id="'course_id' + index" type="checkbox" class="checkbox" :value="course_id"
                    v-model="selectedCourseIDItemsforStudents"
                    @change="courseIDFilterEventChangeforStudents(course_id, $event)">
                  <p v-if="course_id === '-1' || course_id === ''" class="label-text">기타</p>
                  <p v-else class="label-text">{{ course_id }}</p>
                  <!-- <p class="label-text">{{course_id}}</p> -->
                </label>
              </li>
            </ul>
          </transition>
          <!-- 분반 필터 한 개 끝 -->
        </div>
      </div>
      <!-- 전체 filter 끝 -->


      <!-- 과목별 Filter -->
      <div v-show="getRouteType() === 2" class="filter-box">
        <div class="filter-title-box">
          <div class="title">필터</div>
          <v-btn class="init" variant="outlined" v-on:click="resetFilterforCourse" color="#f5d6de">초기화</v-btn>
        </div>
        <div class="filter-container">
          <!-- 과목명 필터 한 개 시작 -->
          <div class=types :class="[this.coursenameDropped ? 'types-focused' : 'types-unfocused']">
            <svg id="type-svg" xmlns="http://www.w3.org/2000/svg" v-show="this.coursenameDropped" width="24" height="25"
              viewBox="0 0 24 25" fill="none">
              <path
                d="M12 6.55337V20.8025M5 8.75464C6.26578 8.95067 7.67778 9.27657 9 9.78788M5 12.7546C5.63949 12.8537 6.3163 12.9859 7 13.1584M3.99433 3.51127C6.21271 3.76195 9.19313 4.43632 11.3168 5.92445C11.725 6.21045 12.275 6.21045 12.6832 5.92445C14.8069 4.43632 17.7873 3.76195 20.0057 3.51127C21.1036 3.38721 22 4.30402 22 5.43518V16.7C22 17.8311 21.1036 18.7483 20.0057 18.8723C17.7873 19.123 14.8069 19.7974 12.6832 21.2855C12.275 21.5715 11.725 21.5715 11.3168 21.2855C9.19313 19.7974 6.21271 19.123 3.99433 18.8723C2.89642 18.7483 2 17.8311 2 16.7V5.43518C2 4.30402 2.89642 3.38721 3.99433 3.51127Z"
                stroke="#910024" stroke-width="1.5" stroke-linecap="round" />
            </svg>
            <svg id="type-svg" xmlns="http://www.w3.org/2000/svg" v-show="!this.coursenameDropped" width="24"
              height="25" viewBox="0 0 24 25" fill="none">
              <path
                d="M12 6.55337V20.8025M5 8.75464C6.26578 8.95067 7.67778 9.27657 9 9.78788M5 12.7546C5.63949 12.8537 6.3163 12.9859 7 13.1584M3.99433 3.51127C6.21271 3.76195 9.19313 4.43632 11.3168 5.92445C11.725 6.21045 12.275 6.21045 12.6832 5.92445C14.8069 4.43632 17.7873 3.76195 20.0057 3.51127C21.1036 3.38721 22 4.30402 22 5.43518V16.7C22 17.8311 21.1036 18.7483 20.0057 18.8723C17.7873 19.123 14.8069 19.7974 12.6832 21.2855C12.275 21.5715 11.725 21.5715 11.3168 21.2855C9.19313 19.7974 6.21271 19.123 3.99433 18.8723C2.89642 18.7483 2 17.8311 2 16.7V5.43518C2 4.30402 2.89642 3.38721 3.99433 3.51127Z"
                stroke="#262626" stroke-width="1.5" stroke-linecap="round" />
            </svg>
            <p class="type-title">
              과목
            </p>
            <button class="drop-btn"><i class="drop-btn-container" v-on:click="coursenamebtnclick">
                <svg class="toggle-btn" v-show="this.coursenameDropped" xmlns="http://www.w3.org/2000/svg" width="12"
                  height="8" viewBox="0 0 12 8" fill="none">
                  <path d="M1 6.5L5.29289 2.20711C5.68342 1.81658 6.31658 1.81658 6.70711 2.20711L11 6.5"
                    stroke="#910024" stroke-width="2" stroke-linecap="round" />
                </svg>
                <svg class="toggle-btn" v-show="!this.coursenameDropped" xmlns="http://www.w3.org/2000/svg" width="13"
                  height="7" viewBox="0 0 13 7" fill="none">
                  <path d="M11.4521 1L7.15925 5.29289C6.76873 5.68342 6.13557 5.68342 5.74504 5.29289L1.45215 0.999999"
                    stroke="#CDCDCD" stroke-width="2" stroke-linecap="round" />
                </svg>
              </i></button>
          </div>
          <transition name="slide">
            <ul class="year-filter no-dot" v-if="coursenameDropped">
              <li class="item" v-for="(course, index) in courseFilterCourseNameCheckbox" :key="index">
                <label :for="'course' + index + 'course'" class="checkbox-label">
                  <input :id="'course' + index + 'course'" type="checkbox" class="checkbox" :value="course.course_id"
                    :checked="isCheckedforCourse(course.course_id)"
                    @change="courseNameFilterEventChangeforCourse(course.course_id, $event)">
                  <p v-if="course.course_id === '-1' || course.course_id === ''" class="label-text">기타</p>
                  <p v-else class="label-text">{{ course.course_name }} ({{ course.course_id }})</p>

                </label>
              </li>
            </ul>
          </transition>
          <!-- 과목명 필터 한 개 끝 -->
        </div>
      </div>
      <!-- 과목별 filter 끝 -->

      <!-- 학과별 Filter -->
      <div v-show="getRouteType() === 3" class="filter-box">
        <div class="filter-title-box">
          <div class="title">필터</div>
          <v-btn class="init" variant="outlined" v-on:click="resetFilterforDepartment" color="#f5d6de">초기화</v-btn>
        </div>
        <div class="filter-container">
          <!-- year 필터 한 개 시작 -->
          <div class=types :class="[this.yearDropped ? 'types-focused' : 'types-unfocused']">
            <svg v-show="this.yearDropped" id="type-svg" xmlns="http://www.w3.org/2000/svg" width="24" height="24"
              viewBox="0 0 24 24" fill="none">
              <path
                d="M3 9V18C3 20.2091 4.79086 22 7 22H17C19.2091 22 21 20.2091 21 18V9M3 9V7.5C3 5.29086 4.79086 3.5 7 3.5H17C19.2091 3.5 21 5.29086 21 7.5V9M3 9H21M16 2V5M8 2V5"
                stroke="#910024" stroke-width="1.5" stroke-linecap="round" />
            </svg>
            <svg v-show="!this.yearDropped" id="type-svg" xmlns="http://www.w3.org/2000/svg" width="24" height="24"
              viewBox="0 0 24 24" fill="none">
              <path
                d="M3 9V18C3 20.2091 4.79086 22 7 22H17C19.2091 22 21 20.2091 21 18V9M3 9V7.5C3 5.29086 4.79086 3.5 7 3.5H17C19.2091 3.5 21 5.29086 21 7.5V9M3 9H21M16 2V5M8 2V5"
                stroke="#262626" stroke-width="1.5" stroke-linecap="round" />
            </svg>
            <p class="type-title">
              연도
            </p>
            <button class="drop-btn"><i class="drop-btn-container" v-on:click="yearbtnclick">
                <svg class="toggle-btn" v-show="this.yearDropped" xmlns="http://www.w3.org/2000/svg" width="12"
                  height="8" viewBox="0 0 12 8" fill="none">
                  <path d="M1 6.5L5.29289 2.20711C5.68342 1.81658 6.31658 1.81658 6.70711 2.20711L11 6.5"
                    stroke="#910024" stroke-width="2" stroke-linecap="round" />
                </svg>
                <svg class="toggle-btn" v-show="!this.yearDropped" xmlns="http://www.w3.org/2000/svg" width="13"
                  height="7" viewBox="0 0 13 7" fill="none">
                  <path d="M11.4521 1L7.15925 5.29289C6.76873 5.68342 6.13557 5.68342 5.74504 5.29289L1.45215 0.999999"
                    stroke="#CDCDCD" stroke-width="2" stroke-linecap="round" />
                </svg>
              </i></button>
          </div>
          <transition name="slide">
            <ul class="year-filter no-dot" v-if="yearDropped">
              <li class="item" v-for="(year, index) in departmentFilterYearsCheckbox">
                <label :for="'year' + index + 'department'" class="checkbox-label">
                  <input :id="'year' + index + 'department'" type="checkbox" class="checkbox" :value="year"
                    v-model="selectedYearItemsforDepartment" @change="yearFilterEventChangeforDepartment(year, $event)">
                  <p v-if="year === '-1' || year === ''" class="label-text">기타</p>
                  <p v-else class="label-text">{{ year }}</p>
                </label>
              </li>
            </ul>
          </transition>
          <!-- year 필터 한 개 끝 -->

          <!-- 학기 필터 한 개 시작 -->
          <div class=types :class="[this.semesterDropped ? 'types-focused' : 'types-unfocused']">

            <svg v-show="this.semesterDropped" id="type-svg" xmlns="http://www.w3.org/2000/svg" width="24" height="25"
              viewBox="0 0 24 25" fill="none">
              <path
                d="M7.9405 9.5H11.9109M7.9405 13.5H15.8812M7.9405 17.5H15.8812M15.8808 2.5V5.5M7.94002 2.5V5.5M6.94791 4H16.8738C19.0666 4 20.8442 5.79086 20.8442 8V18.5C20.8442 20.7091 19.0666 22.5 16.8738 22.5H6.94791C4.75513 22.5 2.97754 20.7091 2.97754 18.5V8C2.97754 5.79086 4.75513 4 6.94791 4Z"
                stroke="#910024" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <svg v-show="!this.semesterDropped" id="type-svg" xmlns="http://www.w3.org/2000/svg" width="24" height="25"
              viewBox="0 0 24 25" fill="none">
              <path
                d="M7.9405 9.5H11.9109M7.9405 13.5H15.8812M7.9405 17.5H15.8812M15.8808 2.5V5.5M7.94002 2.5V5.5M6.94791 4H16.8738C19.0666 4 20.8442 5.79086 20.8442 8V18.5C20.8442 20.7091 19.0666 22.5 16.8738 22.5H6.94791C4.75513 22.5 2.97754 20.7091 2.97754 18.5V8C2.97754 5.79086 4.75513 4 6.94791 4Z"
                stroke="#262626" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <p class="type-title">
              학기
            </p>
            <button class="drop-btn"><i class="drop-btn-container" v-on:click="semesterbtnclick">
                <svg class="toggle-btn" v-show="this.semesterDropped" xmlns="http://www.w3.org/2000/svg" width="12"
                  height="8" viewBox="0 0 12 8" fill="none">
                  <path d="M1 6.5L5.29289 2.20711C5.68342 1.81658 6.31658 1.81658 6.70711 2.20711L11 6.5"
                    stroke="#910024" stroke-width="2" stroke-linecap="round" />
                </svg>
                <svg class="toggle-btn" v-show="!this.semesterDropped" xmlns="http://www.w3.org/2000/svg" width="13"
                  height="7" viewBox="0 0 13 7" fill="none">
                  <path d="M11.4521 1L7.15925 5.29289C6.76873 5.68342 6.13557 5.68342 5.74504 5.29289L1.45215 0.999999"
                    stroke="#CDCDCD" stroke-width="2" stroke-linecap="round" />
                </svg>
              </i></button>
          </div>
          <transition name="slide">
            <ul class="year-filter no-dot" v-if="semesterDropped">
              <li class="item" v-for="(semester, index) in departmentFilterSemesterCheckbox" :key="index">
                <label :for="'semester' + index + 'department'" class="checkbox-label">
                  <input :id="'semester' + index + 'department'" type="checkbox" class="checkbox" :value="semester"
                    v-model="selectedSemesterItemsforDepartment"
                    @change="semesterFilterEventChangeforDepartment(semester, $event)">
                  <p v-if="semester === '-1' || semester === ''" class="label-text">기타</p>
                  <p v-else class="label-text">{{ semester }} 학기</p>
                </label>
              </li>
            </ul>
          </transition>
          <!-- 학기 필터 한 개 끝 -->

          <!-- 과목명 필터 한 개 시작 -->
          <div class=types :class="[this.coursenameDropped ? 'types-focused' : 'types-unfocused']">
            <svg id="type-svg" xmlns="http://www.w3.org/2000/svg" v-show="this.coursenameDropped" width="24" height="25"
              viewBox="0 0 24 25" fill="none">
              <path
                d="M12 6.55337V20.8025M5 8.75464C6.26578 8.95067 7.67778 9.27657 9 9.78788M5 12.7546C5.63949 12.8537 6.3163 12.9859 7 13.1584M3.99433 3.51127C6.21271 3.76195 9.19313 4.43632 11.3168 5.92445C11.725 6.21045 12.275 6.21045 12.6832 5.92445C14.8069 4.43632 17.7873 3.76195 20.0057 3.51127C21.1036 3.38721 22 4.30402 22 5.43518V16.7C22 17.8311 21.1036 18.7483 20.0057 18.8723C17.7873 19.123 14.8069 19.7974 12.6832 21.2855C12.275 21.5715 11.725 21.5715 11.3168 21.2855C9.19313 19.7974 6.21271 19.123 3.99433 18.8723C2.89642 18.7483 2 17.8311 2 16.7V5.43518C2 4.30402 2.89642 3.38721 3.99433 3.51127Z"
                stroke="#910024" stroke-width="1.5" stroke-linecap="round" />
            </svg>
            <svg id="type-svg" xmlns="http://www.w3.org/2000/svg" v-show="!this.coursenameDropped" width="24"
              height="25" viewBox="0 0 24 25" fill="none">
              <path
                d="M12 6.55337V20.8025M5 8.75464C6.26578 8.95067 7.67778 9.27657 9 9.78788M5 12.7546C5.63949 12.8537 6.3163 12.9859 7 13.1584M3.99433 3.51127C6.21271 3.76195 9.19313 4.43632 11.3168 5.92445C11.725 6.21045 12.275 6.21045 12.6832 5.92445C14.8069 4.43632 17.7873 3.76195 20.0057 3.51127C21.1036 3.38721 22 4.30402 22 5.43518V16.7C22 17.8311 21.1036 18.7483 20.0057 18.8723C17.7873 19.123 14.8069 19.7974 12.6832 21.2855C12.275 21.5715 11.725 21.5715 11.3168 21.2855C9.19313 19.7974 6.21271 19.123 3.99433 18.8723C2.89642 18.7483 2 17.8311 2 16.7V5.43518C2 4.30402 2.89642 3.38721 3.99433 3.51127Z"
                stroke="#262626" stroke-width="1.5" stroke-linecap="round" />
            </svg>
            <p class="type-title">
              학과
            </p>
            <button class="drop-btn"><i class="drop-btn-container" v-on:click="coursenamebtnclick">
                <svg class="toggle-btn" v-show="this.coursenameDropped" xmlns="http://www.w3.org/2000/svg" width="12"
                  height="8" viewBox="0 0 12 8" fill="none">
                  <path d="M1 6.5L5.29289 2.20711C5.68342 1.81658 6.31658 1.81658 6.70711 2.20711L11 6.5"
                    stroke="#910024" stroke-width="2" stroke-linecap="round" />
                </svg>
                <svg class="toggle-btn" v-show="!this.coursenameDropped" xmlns="http://www.w3.org/2000/svg" width="13"
                  height="7" viewBox="0 0 13 7" fill="none">
                  <path d="M11.4521 1L7.15925 5.29289C6.76873 5.68342 6.13557 5.68342 5.74504 5.29289L1.45215 0.999999"
                    stroke="#CDCDCD" stroke-width="2" stroke-linecap="round" />
                </svg>
              </i></button>
          </div>
          <transition name="slide">
            <ul class="year-filter no-dot" v-if="coursenameDropped">
              <li class="item" v-for="(department, index) in departmentFilterDepartmentCheckbox" :key="index">
                <label :for="'course' + index + 'department'" class="checkbox-label">
                  <input :id="'course' + index + 'department'" type="checkbox" class="checkbox" :value="department"
                    v-model="selectedDepartmentItemsforDepartment"
                    @change="departmentFilterEventChangeforDepartment(department, $event)">
                  <p v-if="department === '기타' || department === ''" class="label-text">기타</p>
                  <p v-else class="label-text">{{ department }}</p>
                </label>
              </li>
            </ul>
          </transition>
          <!-- 학과별 필터 한 개 끝 -->
        </div>
      </div>
      <!-- 전체 filter 끝 -->
    </div>
    <div class="right-split">
      <div class="title">
        {{ titles }}
      </div>
      <StatisticsStudent v-show="$route.path === '/statistics/students'" :course="studentFilteredPosts">
      </StatisticsStudent>
      <StatisticsCourse v-show="$route.path === '/statistics/course'" :course="courseFilteredPosts"></StatisticsCourse>
      <StatisticsDepartment v-show="$route.path === '/statistics/department'" :course="departmentFilteredPosts">
      </StatisticsDepartment>
    </div>
  </div>
</template>

<script>
import { getCourseInfo, getCourseReadMinMaxAvg } from '@/api.js'
import StatisticsCourse from '@/views/StatisticsComponents/StatisticsCourse.vue'
import StatisticsStudent from '@/views/StatisticsComponents/StatisticsStudent.vue'
import StatisticsDepartment from '@/views/StatisticsComponents/StatisticsDepartment.vue'
export default {
  name: 'Statistics',
  components: {
    StatisticsCourse,
    StatisticsStudent,
    StatisticsDepartment
  },
  data() {
    return {
      titles: '',
      yearDropped: false,
      semesterDropped: false,
      coursenameDropped: false,
      courseIdDropped: false,

      // 전체 data
      studentPosts: [],
      studentFilteredPosts: [],
      studentFilteredPostsforYear: [],
      studentFilteredPostsforSemester: [],
      studentFilteredPostsforCourseName: [],
      studentFilteredPostsforCourseID: [],
      studentFilterYearsCheckbox: [],
      studentFilterSemesterCheckbox: [],
      studentFilterCourseNameCheckbox: [],
      studentFilterCourseIDCheckbox: [],
      selectedYearItemsforStudent: [],
      selectedSemesterItemsforStudent: [],
      selectedCourseNameItemsforStudent: [],
      selectedCourseIDItemsforStudents: [],

      // 과목별 data
      coursePosts: [],
      courseFilteredPosts: [],
      courseFilteredPostsforYear: [],
      courseFilteredPostsforSemester: [],
      courseFilteredPostsforCourseName: [],
      courseFilteredPostsforCourseID: [],
      courseFilterYearsCheckbox: [],
      courseFilterSemesterCheckbox: [],
      courseFilterCourseNameCheckbox: [],
      courseFilterCourseIDCheckbox: [],
      selectedYearItemsforCourse: [],
      selectedSemesterItemsforCourse: [],
      selectedCourseNameItemsforCourse: [],
      selectedCourseIDItemsforCourse: [],

      // 학과별 data
      departmentPosts: [],
      departmentFilteredPosts: [],
      departmentFilteredPostsforYear: [],
      departmentFilteredPostsforSemester: [],
      departmentFilteredPostsforDepartment: [],
      departmentFilterYearsCheckbox: [],
      departmentFilterSemesterCheckbox: [],
      departmentFilterDepartmentCheckbox: [],
      selectedYearItemsforDepartment: [],
      selectedSemesterItemsforDepartment: [],
      selectedDepartmentItemsforDepartment: [],
    };
  },
  mounted() {
    this.setInit()

  },
  methods: {
    getRouteType() {
      if (this.$route.name === 'StatisticsStudent') {
        return 1
      }
      if (this.$route.name === 'StatisticsCourse') {
        return 2
      }
      if (this.$route.name === 'StatisticsDepartment') {
        return 3
      }
    },

    async setInit() {
      if (this.$route.name === "StatisticsStudent") {
        this.titles = '전체 통계'
      }
      if (this.$route.name === "StatisticsCourse") {
        this.titles = '과목 통계'
      }
      if (this.$route.name === "StatisticsDepartment") {
        this.titles = '학과별 통계'
      }

      // 전체통계
      if (this.studentPosts.length === 0) {
        getCourseReadMinMaxAvg().then(res => {
          this.studentPosts = res.data
          this.studentPosts = this.coursePreprocessingTableData(this.studentPosts)
          this.studentFilteredPosts = this.studentPosts
          this.studentFiltering(this.studentPosts)
          this.studentFilteredPostsforYear = this.studentPosts
          this.studentFilteredPostsforSemester = this.studentPosts
          this.studentFilteredPostsforCourseName = this.studentPosts
          this.studentFilteredPostsforCourseID = this.studentPosts
          this.studentPosts = this.yearSort(this.studentPosts)
        })
      }

      // 과목통계
      if (this.coursePosts.length === 0) {
        getCourseReadMinMaxAvg().then(res => {
          this.coursePosts = res.data
          this.coursePosts = this.coursePreprocessingTableData(this.coursePosts)
          this.courseFilteredPosts = []
          this.courseFiltering(this.coursePosts)
          this.courseFilteredPostsforCourseName = this.coursePosts
          this.coursePosts = this.yearSort(this.coursePosts)
        })
      }

      // 학과통계
      if (this.departmentPosts.length === 0) {
        getCourseInfo().then(res => {
          this.departmentPosts = res.data
          this.departmentPosts = this.departmentPreprocessingTableData(this.departmentPosts)
          this.departmentFilteredPosts = this.departmentPosts
          this.departmentFiltering(this.departmentPosts)
          this.departmentFilteredPostsforYear = this.departmentPosts
          this.departmentFilteredPostsforSemester = this.departmentPosts
          this.departmentFilteredPostsforDepartment = this.departmentPosts
        })
      }
    },

    // 공용
    yearbtnclick() {
      this.yearDropped = !this.yearDropped
    },
    semesterbtnclick() {
      this.semesterDropped = !this.semesterDropped
    },
    coursenamebtnclick() {
      this.coursenameDropped = !this.coursenameDropped
    },
    courseIdbtnclick() {
      this.courseIdDropped = !this.courseIdDropped
    },
    studentFiltering(courses) {
      const yearset = new Set(courses.map(row => row.year));
      this.studentFilterYearsCheckbox = [...yearset];

      const semesterset = new Set(courses.map(row => row.semester));
      this.studentFilterSemesterCheckbox = [...semesterset];

      const courseIDset = new Set(courses.map(row => row.course_id));
      let courseIDArray = [...courseIDset];
      let etcCourseIDs = courseIDArray.filter(id => id === '-1' || id === ''); // 기타 항목
      let sortedCourseIDs = courseIDArray.filter(id => id !== '-1' && id !== '').sort((a, b) => a.localeCompare(b, 'ko', { numeric: true, sensitivity: 'base' })); // 문자 오름차순 정렬
      this.courseFilterCourseIDCheckbox = [...sortedCourseIDs, ...etcCourseIDs]; // 정렬된 배열과 기타 항목 결합

      //const courseset = new Set(courses.map(row=>row.course_name));
      // course 정보에 course id도 추가, 중복 제거 기능 추가
      const courseMap = new Map();
      courses.forEach(student => {
        if (!courseMap.has(student.course_id)) {
          courseMap.set(student.course_id, {
            course_name: student.course_name,
            course_id: student.course_id
          });
        }
      });
      // 정렬 기능 추가
      this.studentFilterCourseNameCheckbox = Array.from(courseMap.values()).sort((a, b) => {
        return a.course_name.localeCompare(b.course_name, 'ko', { numeric: true, sensitivity: 'base' });
      });
    },
    courseFiltering(courses) {
      // course 정보에 course id도 추가, 중복 제거 기능 추가
      const courseMap = new Map();
      courses.forEach(course => {
        if (!courseMap.has(course.course_id)) {
          courseMap.set(course.course_id, {
            course_name: course.course_name,
            course_id: course.course_id
          });
        }
      });

      // 정렬 기능 추가
      this.courseFilterCourseNameCheckbox = Array.from(courseMap.values()).sort((a, b) => {
        return a.course_name.localeCompare(b.course_name, 'ko', { numeric: true, sensitivity: 'base' });
      });
    },

    // 전체 및 과목용 전처리
    coursePreprocessingTableData(data) {
        var li = []
        const groupStats = data.group_stats
        groupStats.forEach(course => {
            var parsedData = new Object()
            // year 값 체크
            if (course.year === '' || !course.year) {
                parsedData.year = '-1';
            } else {
                parsedData.year = course.year;
            }
            parsedData.semester = course.semester;
            parsedData.yearandsemester = course.year + '-' + course.semester;
            parsedData.course_name = course.course_name;
            parsedData.course_id = course.course_id;
            parsedData.prof = course.prof;
            parsedData.ta = course.ta;
            parsedData.students = course.student_count;
            parsedData.commit = course.total_commits;
            parsedData.pr = course.total_prs;
            parsedData.issue = course.total_issues;
            parsedData.star = course.total_stars;
            parsedData.num_repos = course.repository_count;
            parsedData.contributors = course.contributor_count;
            parsedData.commit_min = course.commit_min;
            parsedData.commit_max = course.commit_max;
            parsedData.commit_mean = (parsedData.commit / parsedData.students).toFixed(2);
            parsedData.pr_min = course.pr_min;
            parsedData.pr_max = course.pr_max;
            parsedData.pr_mean = (parsedData.pr / parsedData.students).toFixed(2);
            parsedData.issue_min = course.issue_min;
            parsedData.issue_max = course.issue_max;
            parsedData.issue_mean = (parsedData.issue / parsedData.students).toFixed(2);
            parsedData.num_repos_min = course.num_repos_min;
            parsedData.num_repos_max = course.num_repos_max;
            parsedData.num_repos_mean = (parsedData.num_repos / parsedData.students).toFixed(2);
            parsedData.star_min = course.star_count_min;
            parsedData.star_max = course.star_count_max;
            parsedData.star_mean = (parsedData.star / parsedData.students).toFixed(2);
            parsedData.commit_q1 = course.commit_q1;
            parsedData.commit_q2 = course.commit_q2;
            parsedData.commit_q3 = course.commit_q3;
            parsedData.commit_std = course.commit_std.toFixed(2);;
            parsedData.pr_q1 = course.pr_q1;
            parsedData.pr_q2 = course.pr_q2;
            parsedData.pr_q3 = course.pr_q3;
            parsedData.pr_std = course.pr_std.toFixed(2);;
            parsedData.issue_q1 = course.issue_q1;
            parsedData.issue_q2 = course.issue_q2;
            parsedData.issue_q3 = course.issue_q3;
            parsedData.issue_std = course.issue_std.toFixed(2);;
            parsedData.num_repos_q1 = course.num_repos_q1;
            parsedData.num_repos_q2 = course.num_repos_q2;
            parsedData.num_repos_q3 = course.num_repos_q3;
            parsedData.num_repos_std = course.num_repos_std.toFixed(2);;
            parsedData.star_q1 = course.star_q1;
            parsedData.star_q2 = course.star_q2;
            parsedData.star_q3 = course.star_q3;
            parsedData.star_std = course.star_std.toFixed(2);;

            li.push(parsedData);
        });
        console.log("coursePreprocessingTableData", li);

        return li;
    },




    // 학과용 전처리
    departmentPreprocessingTableData(datalist) {
      const li = [];
      const departmentSet = new Set(datalist.map(row => row.department));
      const uniqueDepartments = [...departmentSet];

      uniqueDepartments.forEach(department => {
        li.push({
          department: department,
          years: {},
          departmentByYear: {}, // 새로운 구조 추가
          total: {
            students: 0,
            commits: [],
            prs: [],
            issues: [],
            num_repos: [],
            stars: [],
            commit_stats: null,
            pr_stats: null,
            issue_stats: null,
            num_repos_stats: null,
            stars_stats: null,
          },
          ids: new Set(),
        });
      });
    
      datalist.forEach(element => {
        let departmentIndex = uniqueDepartments.indexOf(element.department);
        let departmentData = li[departmentIndex];
      
        // year와 semester 처리, 값이 없으면 -1로 기본 설정
        const year = element.year === '' ? -1 : element.year;
        const semester = element.semester === '' ? -1 : element.semester;
      
        // `years` 데이터 처리
        if (!departmentData.years[year]) {
          departmentData.years[year] = {
            year: year,
            semesters: {},
            commit_stats: null,
            pr_stats: null,
            issue_stats: null,
            num_repos_stats: null,
            stars_stats: null,
          };
        }
      
        if (!departmentData.years[year].semesters[semester]) {
          departmentData.years[year].semesters[semester] = {
            students: 0,
            commits: [],
            prs: [],
            issues: [],
            num_repos: [],
            stars: [],
            commit_stats: null,
            pr_stats: null,
            issue_stats: null,
            num_repos_stats: null,
            stars_stats: null,
            ids: new Set(),
          };
        }
      
        let semesterData = departmentData.years[year].semesters[semester];
      
        if (!semesterData.ids.has(element.id)) {
          semesterData.students += 1;
          semesterData.ids.add(element.id);
        }
        semesterData.commits.push(element.commit);
        semesterData.prs.push(element.pr);
        semesterData.issues.push(element.issue);
        semesterData.num_repos.push(element.num_repos);
        semesterData.stars.push(element.star_count);
      
        // 전체 통계 업데이트
        if (!departmentData.ids.has(element.id)) {
          departmentData.total.students += 1;
          departmentData.ids.add(element.id);
        }
        departmentData.total.commits.push(element.commit);
        departmentData.total.prs.push(element.pr);
        departmentData.total.issues.push(element.issue);
        departmentData.total.num_repos.push(element.num_repos);
        departmentData.total.stars.push(element.star_count);
      
        // `departmentByYear` 데이터 처리
        if (!departmentData.departmentByYear[year]) {
          departmentData.departmentByYear[year] = {
            students: 0,
            commits: [],
            prs: [],
            issues: [],
            num_repos: [],
            stars: [],
            commit_stats: null,
            pr_stats: null,
            issue_stats: null,
            num_repos_stats: null,
            stars_stats: null,
          };
        }
      
        let departmentYearData = departmentData.departmentByYear[year];
      
        if (!departmentYearData.ids) {
          departmentYearData.ids = new Set();
        }
      
        if (!departmentYearData.ids.has(element.id)) {
          departmentYearData.students += 1;
          departmentYearData.ids.add(element.id);
        }
        departmentYearData.commits.push(element.commit);
        departmentYearData.prs.push(element.pr);
        departmentYearData.issues.push(element.issue);
        departmentYearData.num_repos.push(element.num_repos);
        departmentYearData.stars.push(element.star_count);
      });
    
      // 통계 계산
      li.forEach(departmentData => {
        Object.keys(departmentData.years).forEach(year => {
          let yearData = departmentData.years[year];
          Object.keys(yearData.semesters).forEach(semester => {
            let semesterData = yearData.semesters[semester];
            semesterData.commit_stats = calculateStats(semesterData.commits);
            semesterData.pr_stats = calculateStats(semesterData.prs);
            semesterData.issue_stats = calculateStats(semesterData.issues);
            semesterData.num_repos_stats = calculateStats(semesterData.num_repos);
            semesterData.stars_stats = calculateStats(semesterData.stars);
          });
        });
      
        departmentData.total.commit_stats = calculateStats(departmentData.total.commits);
        departmentData.total.pr_stats = calculateStats(departmentData.total.prs);
        departmentData.total.issue_stats = calculateStats(departmentData.total.issues);
        departmentData.total.num_repos_stats = calculateStats(departmentData.total.num_repos);
        departmentData.total.stars_stats = calculateStats(departmentData.total.stars);
      
        // `departmentByYear` 통계 계산
        Object.keys(departmentData.departmentByYear).forEach(year => {
          let yearData = departmentData.departmentByYear[year];
          yearData.commit_stats = calculateStats(yearData.commits);
          yearData.pr_stats = calculateStats(yearData.prs);
          yearData.issue_stats = calculateStats(yearData.issues);
          yearData.num_repos_stats = calculateStats(yearData.num_repos);
          yearData.stars_stats = calculateStats(yearData.stars);
          delete yearData.ids;  // 임시 ids 세트 삭제
        });
      
        delete departmentData.ids;  // 임시 ids 세트 삭제
      });
    
      return li;
    
      // 통계 계산 유틸리티 함수
      function calculateStats(arr) {
        arr.sort((a, b) => a - b);
        const n = arr.length;
      
        const sum = arr.reduce((acc, val) => acc + val, 0);
        const mean = (sum / n).toFixed(2);
        const variance = (arr.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / n).toFixed(2);
        const stdDev = Math.sqrt(variance).toFixed(2);
        const max = arr[Math.floor((n - 1) * 1)];
        const min = arr[Math.floor((n - 1) * 0)];
        const q1 = arr[Math.floor((n - 1) * 0.25)];
        const median = arr[Math.floor((n - 1) * 0.5)];
        const q3 = arr[Math.floor((n - 1) * 0.75)];
      
        return {
          sum: sum,
          max: max,
          min: min,
          q1: q1,
          median: median,
          q3: q3,
          mean: mean,
          variance: variance,
          stdDev: stdDev,
        };
      }
    },

    yearSort(li) {
      li.sort(function (a, b) {
        if (!a.year) {
          a.year = -1
        }
        if (!b.year) {
          b.year = -1
        }
        return b.year - a.year
      });
      return li
    },
    yearandCommitSort(li) {
      li.sort(function (a, b) {
        // year 값이 없는 경우 -1로 설정
        const yearA = a.year || -1;
        const yearB = b.year || -1;

        // year가 같은 경우 commit 값을 기준으로 정렬
        if (yearA === yearB) {
          return b.commit - a.commit;
        }

        // year를 기준으로 정렬
        return yearB - yearA;
      });
      return li;
    },



    /////////////////////////
    // 전체용 필터
    /////////////////////////
    combineFilterDataforStudent() {
      const allData = [this.studentFilteredPostsforYear, this.studentFilteredPostsforSemester, this.studentFilteredPostsforCourseName, this.studentFilteredPostsforCourseID];
      if (allData.length === 0) return this.studentPosts;

      let common = allData[0];

      for (let i = 1; i < allData.length; i++) {
        common = common.filter(item1 =>
          allData[i].some(item2 => item1.year === item2.year && item1.semester === item2.semester && item1.course_id === item2.course_id)
        );
      }
      return common;
    },
    yearFilterEventChangeforStudent(item, event) {
      if (this.selectedYearItemsforStudent.length === 0) {
        this.studentFilteredPostsforYear = this.studentPosts
      } else {
        this.studentFilteredPostsforYear = this.studentPosts.filter(item => this.selectedYearItemsforStudent.includes(item.year));
      }
      this.studentFilteredPosts = this.combineFilterDataforStudent()
    },
    semesterFilterEventChangeforStudent(item, event) {
      if (this.selectedSemesterItemsforStudent.length === 0) {
        this.studentFilteredPostsforSemester = this.studentPosts
      } else {
        this.studentFilteredPostsforSemester = this.studentPosts.filter(item => this.selectedSemesterItemsforStudent.includes(item.semester));
      }
      this.studentFilteredPosts = this.combineFilterDataforStudent()
    },
    courseNameFilterEventChangeforStudent(item, event) {
      if (this.selectedCourseNameItemsforStudent.length === 0) {
        this.studentFilteredPostsforCourseName = this.studentPosts
      } else {
        this.studentFilteredPostsforCourseName = this.studentPosts.filter(item => this.selectedCourseNameItemsforStudent.includes(item.course_name));
      }
      this.studentFilteredPosts = this.combineFilterDataforStudent()
    },
    courseIDFilterEventChangeforStudents(item, event) {
      if (this.selectedCourseIDItemsforStudents.length === 0) {
        this.studentFilteredPostsforCourseID = this.studentPosts
      } else {
        this.studentFilteredPostsforCourseID = this.studentPosts.filter(item => {
          // 선택된 마지막 두 자리 값과 원래 course_id의 마지막 두 자리를 비교하여 필터링
          const lastTwoDigits = item.course_id.split('-').pop(); // 현재 item의 course_id의 마지막 두 자리
          return this.selectedCourseIDItemsforStudents.includes(lastTwoDigits);
        });
      }
      this.studentFilteredPosts = this.combineFilterDataforStudent()
    },
    resetFilterforStudent() {
      this.selectedYearItemsforStudent = []
      this.selectedSemesterItemsforStudent = []
      this.selectedCourseNameItemsforStudent = []
      this.selectedCourseIDItemsforStudents = []
      this.studentFilteredPostsforYear = this.studentPosts
      this.studentFilteredPostsforSemester = this.studentPosts
      this.studentFilteredPostsforCourseName = this.studentPosts
      this.studentFilteredPostsforCourseID = this.studentPosts
      this.studentFilteredPosts = this.studentPosts
    },

    //////////////////
    // 과목용 필터
    //////////////////
    courseNameFilterEventChangeforCourse(course_id, event) {
      if (this.selectedCourseNameItemsforCourse.includes(course_id)) {
        var idx = this.selectedCourseNameItemsforCourse.indexOf(course_id);
        this.selectedCourseNameItemsforCourse.splice(idx, 1);
      } else {
        this.selectedCourseNameItemsforCourse = [];
        this.selectedCourseNameItemsforCourse.push(course_id);
      }

      if (this.selectedCourseNameItemsforCourse.length === 0) {
        this.courseFilteredPostsforCourseName = [];
      } else {
        this.courseFilteredPostsforCourseName = this.coursePosts.filter(item => this.selectedCourseNameItemsforCourse.includes(item.course_id));
      }

      this.courseFilteredPosts = this.combineFilterDataforCourse();
    },
    combineFilterDataforCourse() {

      const allData = [this.courseFilteredPostsforCourseName];

      let common = allData[0];

      for (let i = 1; i < allData.length; i++) {
        common = common.filter(item1 =>
          allData[i].some(item2 => item1.year === item2.year && item1.semester === item2.semester && item1.course_id === item2.course_id)
        );
      }
      return common;
    },
    resetFilterforCourse() {
      this.selectedYearItemsforCourse = []
      this.selectedSemesterItemsforCourse = []
      this.selectedCourseNameItemsforCourse = []
      this.courseFilteredPostsforCourseName = []
      this.courseFilteredPosts = []
    },
    isCheckedforCourse(courseID) {
      return this.selectedCourseNameItemsforCourse.includes(courseID)
    },

    /////////////////////////
    // 학과용 필터
    /////////////////////////
    departmentFiltering(departmentData) {
      const yearset = new Set(departmentData.flatMap((row) => Object.keys(row.years)));
      this.departmentFilterYearsCheckbox = [...yearset];
      const semesterset = new Set(departmentData.flatMap((row) => Object.values(row.years).flatMap((year) => Object.keys(year.semesters))));
      this.departmentFilterSemesterCheckbox = [...semesterset];
      const departmentset = new Set(departmentData.map((row) => row.department));
      this.departmentFilterDepartmentCheckbox = [...departmentset];
    },

    combineFilterDataforDepartment() {
      let common = this.departmentPosts; // 초기 데이터 설정

      // 연도와 학기 필터링을 동시에 고려하여 total 및 departmentByYear 업데이트
      if (this.selectedYearItemsforDepartment.length > 0 || this.selectedSemesterItemsforDepartment.length > 0) {
        common = common.map(department => {
          let filteredDepartment = {
            ...department,
            total: { ...department.total },
            years: { ...department.years },
            departmentByYear: {} // 선택된 연도만 포함하도록 초기화
          };

          filteredDepartment.total.commits = [];
          filteredDepartment.total.prs = [];
          filteredDepartment.total.issues = [];
          filteredDepartment.total.num_repos = [];
          filteredDepartment.total.stars = [];
          filteredDepartment.total.students = 0;

          // 연도 및 학기별로 필터링 적용
          Object.keys(department.departmentByYear).forEach(year => {
            if (this.selectedYearItemsforDepartment.length === 0 || this.selectedYearItemsforDepartment.includes(year)) {
              let yearData = { ...department.departmentByYear[year] };
              yearData.students = 0;
              yearData.commits = [];
              yearData.prs = [];
              yearData.issues = [];
              yearData.num_repos = [];
              yearData.stars = [];

              // 학기 필터링
              Object.keys(department.years[year]?.semesters || {}).forEach(semester => {
                if (this.selectedSemesterItemsforDepartment.length === 0 || this.selectedSemesterItemsforDepartment.includes(semester)) {
                  const semesterData = department.years[year].semesters[semester];
                  yearData.commits.push(...semesterData.commits);
                  yearData.prs.push(...semesterData.prs);
                  yearData.issues.push(...semesterData.issues);
                  yearData.num_repos.push(...semesterData.num_repos);
                  yearData.stars.push(...semesterData.stars);
                  yearData.students += semesterData.students;

                  // 전체 통계에도 추가
                  filteredDepartment.total.commits.push(...semesterData.commits);
                  filteredDepartment.total.prs.push(...semesterData.prs);
                  filteredDepartment.total.issues.push(...semesterData.issues);
                  filteredDepartment.total.num_repos.push(...semesterData.num_repos);
                  filteredDepartment.total.stars.push(...semesterData.stars);
                  filteredDepartment.total.students += semesterData.students;
                }
              });

              // 연도별 통계 계산
              yearData.commit_stats = calculateStats(yearData.commits);
              yearData.pr_stats = calculateStats(yearData.prs);
              yearData.issue_stats = calculateStats(yearData.issues);
              yearData.num_repos_stats = calculateStats(yearData.num_repos);
              yearData.stars_stats = calculateStats(yearData.stars);

              // 선택된 연도만 포함되도록 필터링된 departmentByYear 업데이트
              filteredDepartment.departmentByYear[year] = yearData;
            }
          });
          return filteredDepartment;
        });
      }

      // 학과 필터링
      if (this.selectedDepartmentItemsforDepartment.length > 0) {
        common = common.filter(department =>
          this.selectedDepartmentItemsforDepartment.includes(department.department)
        );
      }
      return common;
    },

    yearFilterEventChangeforDepartment(item, event) {
      if (this.selectedYearItemsforDepartment.length === 0) {
        this.departmentFilteredPostsforYear = this.departmentPosts;
      } else {
        this.departmentFilteredPostsforYear = this.departmentPosts.filter((department) => {
          // department.years가 정의되어 있는지 확인
          return department.years && Object.keys(department.years).includes(item);
        });
      }
      this.departmentFilteredPosts = this.combineFilterDataforDepartment();
    },
    semesterFilterEventChangeforDepartment(item, event) {
      if (this.selectedSemesterItemsforDepartment.length === 0) {
        this.departmentFilteredPostsforSemester = this.departmentPosts;
      } else {
        this.departmentFilteredPostsforSemester = this.departmentPosts.filter((department) =>
          Object.values(department.years).some((year) =>
            Object.keys(year.semesters).includes(item)
          )
        );
      }
      this.departmentFilteredPosts = this.combineFilterDataforDepartment();
    },
    departmentFilterEventChangeforDepartment(item, event) {
      if (this.selectedDepartmentItemsforDepartment.length === 0) {
        this.departmentFilteredPostsforDepartment = this.departmentPosts;
      } else {
        this.departmentFilteredPostsforDepartment = this.departmentPosts.filter((department) =>
          this.selectedDepartmentItemsforDepartment.includes(department.department)
        );
      }
      this.departmentFilteredPosts = this.combineFilterDataforDepartment();
    },
    resetFilterforDepartment() {
      this.selectedYearItemsforDepartment = [];
      this.selectedSemesterItemsforDepartment = [];
      this.selectedDepartmentItemsforDepartment = [];
      this.departmentFilteredPostsforYear = this.departmentPosts;
      this.departmentFilteredPostsforSemester = this.departmentPosts;
      this.departmentFilteredPostsforDepartment = this.departmentPosts;
      this.departmentFilteredPosts = this.departmentPosts;
    },
  },
  computed: {
    uniqueCourses() {
      // 과목 이름을 기준으로 중복된 항목을 제거
      const seen = new Set();
      return this.studentFilterCourseNameCheckbox.filter(course => {
        if (seen.has(course.course_name)) {
          return false;
        } else {
          seen.add(course.course_name);
          return true;
        }
      });
    },
    uniqueCourseIDs() {
      // 마지막 두 자리만 추출하고 중복을 제거한 배열 반환
      const lastTwoDigitsSet = new Set(this.courseFilterCourseIDCheckbox.map(course_id => {
        return course_id.split('-').pop(); // '-'로 나눈 후, 마지막 부분을 가져옴
      }));

      let courseIDsArray = [...lastTwoDigitsSet]; // Set을 배열로 변환

      // '기타' 항목과 숫자 항목을 분리
      let etcItem = courseIDsArray.filter(id => id === '-1' || id === ''); // 기타 항목 추출
      let sortedItems = courseIDsArray.filter(id => id !== '-1' && id !== '').sort((a, b) => a - b); // 숫자 항목 정렬

      // 정렬된 숫자 항목 뒤에 기타 항목 추가
      return [...sortedItems, ...etcItem];
    }
  },
  beforeMount() {
    if (this.$route.fullPath === "/statistics") {
      this.$router.replace('/statistics/students')
    }
  },
  watch: {
    $route(to, from) {
      if (to.path !== from.path) {
        this.setInit()
      }
    },
  }
}
</script>

<style>
.default-container {
  /* position: relative; */
  display: flex;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
  margin-top: 120px;
  height: 120vh;
  background: #FFF;
  overflow: hidden;
  /* Ensure no overflow issues */
}


.left-split {
  margin-left: 320px;
  width: 268px !important;
  min-width: 268px;
  height: inherit;
  border-right: 2px solid;
  border-right-color: #DCE2ED;

  .empty-box {
    width: 100em;
    margin-bottom: 117px;
  }

  .filter-box {
    height: 100%;

    .filter-title-box {
      height: 32px;
      display: flex;
      flex-wrap: nowrap;

      .title {
        font-size: 22px;
        font-weight: 600;

      }

      .init {
        margin-left: auto;
        margin-right: 15px;
        background-color: #FCFCFC !important;
        height: 29px;

        &:hover {
          background: #ffe9eb !important;
        }

        /* &:hover {
          background-color: #CB385C;
          opacity: 0.2;
        } */
        .v-btn__content {
          font-weight: 600 !important;
          color: #CB385C !important;
        }

        &.v-btn--variant-outlined {
          border-radius: 10px;
          border: 1px solid var(--Primary_medium, #CB385C);
        }
      }
    }

    .filter-container {
      /* margin-top:20px; */
      width: 268px;
      height: 100em;
      /* border-left: solid 1px black; */
      border-right: 2px solid;
      border-right-color: #DCE2ED;

      .types {
        display: flex;
        align-items: center;
        height: 60px;
        flex-shrink: 0;
        width: 100%;
        margin-top: 20px;
        vertical-align: center;

        .type-title {
          margin-left: 10px;
          font-size: 18px;
          font-style: normal;
          font-weight: 600;
          line-height: normal;
          /* color:#910024; */
        }
      }

      .types-focused {
        background: var(--Primary_extralight, #FFEAEC);

        .type-title {
          color: #910024;
        }

        border-left: 4px solid var(--Primary_normal, #910024);

        #type-svg {
          margin-left: 16px !important;
        }
      }

      .types-unfocused {
        background: #F8F8F8;

        .type-title {
          color: var(--Black, #262626);
        }
      }
    }
  }
}

.right-split {
  width: 100%;
  margin-right: 320px;
  height: inherit;

  .title {
    font-size: 28px;
    font-weight: 700;
    margin-top: 57px;
    margin-left: 57px;
    height: 33px;
    min-height: 33px;
    margin-bottom: 34px;
  }
}

.no_dot {
  list-style-type: none;
  list-style: none;
}

ul {
  list-style: none;
  padding-left: 0px;
}

.item {
  display: flex;
  width: 100%;
  padding: 10px 10px 10px 20px;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  /* border: solid 1px black; */
}

#type-svg {
  margin-left: 20px;
}

.drop-btn {
  /* margin: 0 auto; */
  width: 30px;
  height: 30px;
  display: inline-flex;
  padding: 13px 10px;
  justify-content: flex-end;
  margin-left: auto;
  margin-right: 20px;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;

  .drop-btn-container {
    width: 30px;
    height: 30px;
    /* margin: 0 auto; */
    text-align: center;
    display: flex;
    /* justify-content: center; */
    vertical-align: center;
    justify-content: flex-end;
    padding-top: 13px;

    .toggle-btn {}
  }
}

.year-filter {
  transform-origin: top;
  transition: transform .2s ease-in-out;
  max-height: 250px;
  overflow-y: auto;
  background: var(--Primary_background, #FFFBFB);
}

.slide-enter {
  transition: transform .0s ease-in-out;
}

.slide-enter-active,
.slide-leave-to {
  transform: scaleY(0);
}

.label-text {
  display: inline;
  margin-left: 13px;
  font-size: 18px;
  font-style: normal;
  font-weight: 500;
  color: var(--Gray400, #949494);
  vertical-align: middle;
  position: relative;
}


/* 기본 체크박스 숨기기 */
input[type="checkbox"] {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  vertical-align: middle;
  position: relative;
  border-radius: 5px;
  width: 20px;
  height: 20px;
  border: 2px solid #FFEAEC;
  background-color: #FFEAEC;
  border-radius: 4px;
  position: relative;
  cursor: pointer;
}

/* 체크된 상태 스타일 */
input[type="checkbox"]:checked {
  background-color: #910024;
  /* 원하는 색상으로 변경 */
  border-color: #910024;
}

input[type="checkbox"]:checked::after {
  content: '';
  vertical-align: middle;
  position: relative;
  border-radius: 5px;
  top: 4px;
  left: 4px;
  width: 10px;
  height: 10px;
  background-color: #FFEAEC;
  border-radius: 2px;
}
</style>
