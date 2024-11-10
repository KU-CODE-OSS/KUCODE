<template>
  <div class="default-container">
    <div class="left-split">
      <div class="empty-box"></div>
      <!-- Course Filter -->
      <div v-show="getRouteType() === 1" class="filter-box">
        <div class="filter-title-box">
          <div class="title">필터</div>
          <v-btn class="init" variant="outlined" v-on:click="resetFilterforCourse" color="#f5d6de">초기화</v-btn>
        </div>
        <div class="filter-container">
          <!-- year 필터 한 개 시작 -->
          <div class=types :class="[this.yearDropped ? 'types-focused' :'types-unfocused']">
            <svg v-show="this.yearDropped" id="type-svg" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M3 9V18C3 20.2091 4.79086 22 7 22H17C19.2091 22 21 20.2091 21 18V9M3 9V7.5C3 5.29086 4.79086 3.5 7 3.5H17C19.2091 3.5 21 5.29086 21 7.5V9M3 9H21M16 2V5M8 2V5" stroke="#910024" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <svg v-show="!this.yearDropped" id="type-svg" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M3 9V18C3 20.2091 4.79086 22 7 22H17C19.2091 22 21 20.2091 21 18V9M3 9V7.5C3 5.29086 4.79086 3.5 7 3.5H17C19.2091 3.5 21 5.29086 21 7.5V9M3 9H21M16 2V5M8 2V5" stroke="#262626" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <p class="type-title">
              연도
            </p>
            <button class="drop-btn"><i class="drop-btn-container" v-on:click="yearbtnclick">
              <svg class="toggle-btn" v-show="this.yearDropped" xmlns="http://www.w3.org/2000/svg" width="12" height="8" viewBox="0 0 12 8" fill="none">
                <path d="M1 6.5L5.29289 2.20711C5.68342 1.81658 6.31658 1.81658 6.70711 2.20711L11 6.5" stroke="#910024" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <svg class="toggle-btn" v-show="!this.yearDropped" xmlns="http://www.w3.org/2000/svg" width="13" height="7" viewBox="0 0 13 7" fill="none">
                <path d="M11.4521 1L7.15925 5.29289C6.76873 5.68342 6.13557 5.68342 5.74504 5.29289L1.45215 0.999999" stroke="#CDCDCD" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </i></button>
          </div>
          <transition name="slide">
            <ul class="year-filter no-dot" v-if="yearDropped">
              <li class="item" v-for="(year, index) in courseFilterYearsCheckbox">
                <label :for="'year' + index" class="checkbox-label">
                  <input :id="'year' + index" type="checkbox" class="checkbox" :value="year" v-model="selectedYearItemsforCourse" @change="yearFilterEventChangeforCourse(year, $event)">
                  <p v-if="year === '-1' || year === ''" class="label-text">기타</p>
                  <p v-else class="label-text">{{year}}</p>
                </label>
              </li>
            </ul>
          </transition>
           <!-- year 필터 한 개 끝 -->

          <!-- 학기 필터 한 개 시작 -->
          <div class=types :class="[this.semesterDropped ? 'types-focused' :'types-unfocused']">

            <svg v-show="this.semesterDropped" id="type-svg"  xmlns="http://www.w3.org/2000/svg" width="24" height="25" viewBox="0 0 24 25" fill="none">
              <path d="M7.9405 9.5H11.9109M7.9405 13.5H15.8812M7.9405 17.5H15.8812M15.8808 2.5V5.5M7.94002 2.5V5.5M6.94791 4H16.8738C19.0666 4 20.8442 5.79086 20.8442 8V18.5C20.8442 20.7091 19.0666 22.5 16.8738 22.5H6.94791C4.75513 22.5 2.97754 20.7091 2.97754 18.5V8C2.97754 5.79086 4.75513 4 6.94791 4Z" stroke="#910024" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-show="!this.semesterDropped" id="type-svg"  xmlns="http://www.w3.org/2000/svg" width="24" height="25" viewBox="0 0 24 25" fill="none">
              <path d="M7.9405 9.5H11.9109M7.9405 13.5H15.8812M7.9405 17.5H15.8812M15.8808 2.5V5.5M7.94002 2.5V5.5M6.94791 4H16.8738C19.0666 4 20.8442 5.79086 20.8442 8V18.5C20.8442 20.7091 19.0666 22.5 16.8738 22.5H6.94791C4.75513 22.5 2.97754 20.7091 2.97754 18.5V8C2.97754 5.79086 4.75513 4 6.94791 4Z" stroke="#262626" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <p class="type-title">
              학기
            </p>
            <button class="drop-btn"><i class="drop-btn-container" v-on:click="semesterbtnclick">
              <svg class="toggle-btn" v-show="this.semesterDropped" xmlns="http://www.w3.org/2000/svg" width="12" height="8" viewBox="0 0 12 8" fill="none">
                <path d="M1 6.5L5.29289 2.20711C5.68342 1.81658 6.31658 1.81658 6.70711 2.20711L11 6.5" stroke="#910024" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <svg class="toggle-btn" v-show="!this.semesterDropped" xmlns="http://www.w3.org/2000/svg" width="13" height="7" viewBox="0 0 13 7" fill="none">
                <path d="M11.4521 1L7.15925 5.29289C6.76873 5.68342 6.13557 5.68342 5.74504 5.29289L1.45215 0.999999" stroke="#CDCDCD" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </i></button>
          </div>
          <transition name="slide">
            <ul class="year-filter no-dot" v-if="semesterDropped">
              <li class="item" v-for="(semester, index) in courseFilterSemesterCheckbox" :key="index">
                <label :for="'semester' + index" class="checkbox-label">
                  <input :id="'semester' + index" type="checkbox" class="checkbox" :value="semester" v-model="selectedSemesterItemsforCourse" @change="semesterFilterEventChangeforCourse(semester, $event)">
                  <p v-if="semester === '-1' || semester === ''" class="label-text">기타</p>
                  <p v-else class="label-text">{{semester}} 학기</p>
                </label>
              </li>
            </ul>
          </transition>
           <!-- 학기 필터 한 개 끝 -->

          <!-- 과목명 필터 한 개 시작 -->
          <div class=types :class="[this.coursenameDropped ? 'types-focused' :'types-unfocused']">
            <svg id="type-svg"  xmlns="http://www.w3.org/2000/svg" v-show="this.coursenameDropped" width="24" height="25" viewBox="0 0 24 25" fill="none">
              <path d="M12 6.55337V20.8025M5 8.75464C6.26578 8.95067 7.67778 9.27657 9 9.78788M5 12.7546C5.63949 12.8537 6.3163 12.9859 7 13.1584M3.99433 3.51127C6.21271 3.76195 9.19313 4.43632 11.3168 5.92445C11.725 6.21045 12.275 6.21045 12.6832 5.92445C14.8069 4.43632 17.7873 3.76195 20.0057 3.51127C21.1036 3.38721 22 4.30402 22 5.43518V16.7C22 17.8311 21.1036 18.7483 20.0057 18.8723C17.7873 19.123 14.8069 19.7974 12.6832 21.2855C12.275 21.5715 11.725 21.5715 11.3168 21.2855C9.19313 19.7974 6.21271 19.123 3.99433 18.8723C2.89642 18.7483 2 17.8311 2 16.7V5.43518C2 4.30402 2.89642 3.38721 3.99433 3.51127Z" stroke="#910024" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <svg id="type-svg"  xmlns="http://www.w3.org/2000/svg" v-show="!this.coursenameDropped" width="24" height="25" viewBox="0 0 24 25" fill="none">
              <path d="M12 6.55337V20.8025M5 8.75464C6.26578 8.95067 7.67778 9.27657 9 9.78788M5 12.7546C5.63949 12.8537 6.3163 12.9859 7 13.1584M3.99433 3.51127C6.21271 3.76195 9.19313 4.43632 11.3168 5.92445C11.725 6.21045 12.275 6.21045 12.6832 5.92445C14.8069 4.43632 17.7873 3.76195 20.0057 3.51127C21.1036 3.38721 22 4.30402 22 5.43518V16.7C22 17.8311 21.1036 18.7483 20.0057 18.8723C17.7873 19.123 14.8069 19.7974 12.6832 21.2855C12.275 21.5715 11.725 21.5715 11.3168 21.2855C9.19313 19.7974 6.21271 19.123 3.99433 18.8723C2.89642 18.7483 2 17.8311 2 16.7V5.43518C2 4.30402 2.89642 3.38721 3.99433 3.51127Z" stroke="#262626" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <p class="type-title">
              과목
            </p>
            <button class="drop-btn"><i class="drop-btn-container" v-on:click="coursenamebtnclick">
              <svg class="toggle-btn" v-show="this.coursenameDropped" xmlns="http://www.w3.org/2000/svg" width="12" height="8" viewBox="0 0 12 8" fill="none">
                <path d="M1 6.5L5.29289 2.20711C5.68342 1.81658 6.31658 1.81658 6.70711 2.20711L11 6.5" stroke="#910024" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <svg class="toggle-btn" v-show="!this.coursenameDropped" xmlns="http://www.w3.org/2000/svg" width="13" height="7" viewBox="0 0 13 7" fill="none">
                <path d="M11.4521 1L7.15925 5.29289C6.76873 5.68342 6.13557 5.68342 5.74504 5.29289L1.45215 0.999999" stroke="#CDCDCD" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </i></button>
          </div>
          <transition name="slide">
            <ul class="year-filter no-dot" v-if="coursenameDropped">
              <li class="item" v-for="(course, index) in uniqueCourses" :key="index">
                <label :for="'course' + index" class="checkbox-label">
                  <input :id="'course' + index" type="checkbox" class="checkbox" :value="course.course_name" v-model="selectedCourseNameItemsforCourse" @change="courseNameFilterEventChangeforCourse(semester, $event)">
                  <!-- <p v-if="course.course_name === '기타' || course.course_name === ''" class="label-text">기타</p>
                  <p v-else class="label-text">{{course.course_name}} ({{course.course_id}})</p> -->
                  <p class="label-text">{{course.course_name}}</p> <!-- course_id 제거 버전-->
                </label>
              </li>
            </ul>
          </transition>
          <!-- 과목명 필터 한 개 끝 -->
          <!-- (과목 탭) 분반 필터 한 개 시작 -->
          <div class=types :class="[this.courseIdDropped ? 'types-focused' :'types-unfocused']">

            <svg v-show="this.courseIdDropped" id="type-svg"  xmlns="http://www.w3.org/2000/svg" width="24" height="25" viewBox="0 0 24 25" fill="none">
              <path d="M7 14s-1 0-1-1 1-4 5-4 5 3 5 4-1 1-1 1zm4-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6m-5.784 6A2.24 2.24 0 0 1 5 13c0-1.355.68-2.75 1.936-3.72A6.3 6.3 0 0 0 5 9c-4 0-5 3-5 4s1 1 1 1zM4.5 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5" stroke="#910024" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-show="!this.courseIdDropped" id="type-svg"  xmlns="http://www.w3.org/2000/svg" width="24" height="25" viewBox="0 0 24 25" fill="none">
              <path d="M7 14s-1 0-1-1 1-4 5-4 5 3 5 4-1 1-1 1zm4-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6m-5.784 6A2.24 2.24 0 0 1 5 13c0-1.355.68-2.75 1.936-3.72A6.3 6.3 0 0 0 5 9c-4 0-5 3-5 4s1 1 1 1zM4.5 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5" stroke="#262626" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <p class="type-title">
              분반
            </p>
            <button class="drop-btn"><i class="drop-btn-container" v-on:click="courseIdbtnclick">
              <svg class="toggle-btn" v-show="this.courseIdDropped" xmlns="http://www.w3.org/2000/svg" width="12" height="8" viewBox="0 0 12 8" fill="none">
                <path d="M1 6.5L5.29289 2.20711C5.68342 1.81658 6.31658 1.81658 6.70711 2.20711L11 6.5" stroke="#910024" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <svg class="toggle-btn" v-show="!this.courseIdDropped" xmlns="http://www.w3.org/2000/svg" width="13" height="7" viewBox="0 0 13 7" fill="none">
                <path d="M11.4521 1L7.15925 5.29289C6.76873 5.68342 6.13557 5.68342 5.74504 5.29289L1.45215 0.999999" stroke="#CDCDCD" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </i></button>
          </div>
          <transition name="slide">
            <ul class="year-filter no-dot" v-if="courseIdDropped">
              <li class="item" v-for="(course_id, index) in uniqueCourseIDs" :key="index">
                <label :for="'course_id' + index" class="checkbox-label">
                  <input :id="'course_id' + index" type="checkbox" class="checkbox" :value="course_id" v-model="selectedCourseIDItemsforCourse" @change="courseIDFilterEventChangeforCourse(course_id, $event)">
                  <p v-if="course_id === '-1' || course_id === ''" class="label-text">기타</p>
                  <p v-else class="label-text">{{course_id}}</p>
                  <!-- <p class="label-text">{{course_id}}</p> -->
                </label>
              </li>
            </ul>
          </transition>
           <!-- 분반 필터 한 개 끝 -->
        </div>
      </div>
      <!-- course filter 끝 -->

      <!-- student Filter -->
      <div v-show="getRouteType() === 2" class="filter-box">
        <div class="filter-title-box">
          <div class="title">필터</div>
          <v-btn class="init" variant="outlined" v-on:click="resetFilterforStudents" color="#f5d6de">초기화</v-btn>
        </div>
        <div class="filter-container">
          <!-- year 필터 한 개 시작 -->
          <div class=types :class="[this.yearDropped ? 'types-focused' :'types-unfocused']">
            <svg v-show="this.yearDropped" id="type-svg" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M3 9V18C3 20.2091 4.79086 22 7 22H17C19.2091 22 21 20.2091 21 18V9M3 9V7.5C3 5.29086 4.79086 3.5 7 3.5H17C19.2091 3.5 21 5.29086 21 7.5V9M3 9H21M16 2V5M8 2V5" stroke="#910024" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <svg v-show="!this.yearDropped" id="type-svg" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M3 9V18C3 20.2091 4.79086 22 7 22H17C19.2091 22 21 20.2091 21 18V9M3 9V7.5C3 5.29086 4.79086 3.5 7 3.5H17C19.2091 3.5 21 5.29086 21 7.5V9M3 9H21M16 2V5M8 2V5" stroke="#262626" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <p class="type-title">
              연도
            </p>
            <button class="drop-btn"><i class="drop-btn-container" v-on:click="yearbtnclick">
              <svg class="toggle-btn" v-show="this.yearDropped" xmlns="http://www.w3.org/2000/svg" width="12" height="8" viewBox="0 0 12 8" fill="none">
                <path d="M1 6.5L5.29289 2.20711C5.68342 1.81658 6.31658 1.81658 6.70711 2.20711L11 6.5" stroke="#910024" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <svg class="toggle-btn" v-show="!this.yearDropped" xmlns="http://www.w3.org/2000/svg" width="13" height="7" viewBox="0 0 13 7" fill="none">
                <path d="M11.4521 1L7.15925 5.29289C6.76873 5.68342 6.13557 5.68342 5.74504 5.29289L1.45215 0.999999" stroke="#CDCDCD" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </i></button>
          </div>
          <transition name="slide">
            <ul class="year-filter no-dot" v-if="yearDropped">
              <li class="item" v-for="(year, index) in studentsFilterYearsCheckbox">
                <label :for="'year-student' + index" class="checkbox-label">
                  <input :id="'year-student' + index" type="checkbox" class="checkbox" :value="year" v-model="selectedYearItemsforStudents" @change="yearFilterEventChangeforStudents(year, $event)">
                  <p v-if="year === '-1' || year === ''" class="label-text">기타</p>
                  <p v-else class="label-text">{{year}}</p>
                </label>
              </li>
            </ul>
          </transition>
           <!-- year 필터 한 개 끝 -->

          <!-- 학기 필터 한 개 시작 -->
          <div class=types :class="[this.semesterDropped ? 'types-focused' :'types-unfocused']">

            <svg v-show="this.semesterDropped" id="type-svg"  xmlns="http://www.w3.org/2000/svg" width="24" height="25" viewBox="0 0 24 25" fill="none">
              <path d="M7.9405 9.5H11.9109M7.9405 13.5H15.8812M7.9405 17.5H15.8812M15.8808 2.5V5.5M7.94002 2.5V5.5M6.94791 4H16.8738C19.0666 4 20.8442 5.79086 20.8442 8V18.5C20.8442 20.7091 19.0666 22.5 16.8738 22.5H6.94791C4.75513 22.5 2.97754 20.7091 2.97754 18.5V8C2.97754 5.79086 4.75513 4 6.94791 4Z" stroke="#910024" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-show="!this.semesterDropped" id="type-svg"  xmlns="http://www.w3.org/2000/svg" width="24" height="25" viewBox="0 0 24 25" fill="none">
              <path d="M7.9405 9.5H11.9109M7.9405 13.5H15.8812M7.9405 17.5H15.8812M15.8808 2.5V5.5M7.94002 2.5V5.5M6.94791 4H16.8738C19.0666 4 20.8442 5.79086 20.8442 8V18.5C20.8442 20.7091 19.0666 22.5 16.8738 22.5H6.94791C4.75513 22.5 2.97754 20.7091 2.97754 18.5V8C2.97754 5.79086 4.75513 4 6.94791 4Z" stroke="#262626" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <p class="type-title">
              학기
            </p>
            <button class="drop-btn"><i class="drop-btn-container" v-on:click="semesterbtnclick">
              <svg class="toggle-btn" v-show="this.semesterDropped" xmlns="http://www.w3.org/2000/svg" width="12" height="8" viewBox="0 0 12 8" fill="none">
                <path d="M1 6.5L5.29289 2.20711C5.68342 1.81658 6.31658 1.81658 6.70711 2.20711L11 6.5" stroke="#910024" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <svg class="toggle-btn" v-show="!this.semesterDropped" xmlns="http://www.w3.org/2000/svg" width="13" height="7" viewBox="0 0 13 7" fill="none">
                <path d="M11.4521 1L7.15925 5.29289C6.76873 5.68342 6.13557 5.68342 5.74504 5.29289L1.45215 0.999999" stroke="#CDCDCD" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </i></button>
          </div>
          <transition name="slide">
            <ul class="year-filter no-dot" v-if="semesterDropped">
              <li class="item" v-for="(semester, index) in studentsFilterSemesterCheckbox" :key="index">
                <label :for="'semester-student' + index" class="checkbox-label">
                  <input :id="'semester-student' + index" type="checkbox" class="checkbox" :value="semester" v-model="selectedSemesterItemsforStudents" @change="semesterFilterEventChangeforStudents(semester, $event)">
                  <p v-if="semester === '-1' || semester === ''" class="label-text">기타</p>
                  <p v-else class="label-text">{{semester}} 학기</p>
                </label>
              </li>
            </ul>
          </transition>
           <!-- 학기 필터 한 개 끝 -->

          <!-- 과목명 필터 한 개 시작 -->
          <div class=types :class="[this.coursenameDropped ? 'types-focused' :'types-unfocused']">
            <svg id="type-svg"  xmlns="http://www.w3.org/2000/svg" v-show="this.coursenameDropped" width="24" height="25" viewBox="0 0 24 25" fill="none">
              <path d="M12 6.55337V20.8025M5 8.75464C6.26578 8.95067 7.67778 9.27657 9 9.78788M5 12.7546C5.63949 12.8537 6.3163 12.9859 7 13.1584M3.99433 3.51127C6.21271 3.76195 9.19313 4.43632 11.3168 5.92445C11.725 6.21045 12.275 6.21045 12.6832 5.92445C14.8069 4.43632 17.7873 3.76195 20.0057 3.51127C21.1036 3.38721 22 4.30402 22 5.43518V16.7C22 17.8311 21.1036 18.7483 20.0057 18.8723C17.7873 19.123 14.8069 19.7974 12.6832 21.2855C12.275 21.5715 11.725 21.5715 11.3168 21.2855C9.19313 19.7974 6.21271 19.123 3.99433 18.8723C2.89642 18.7483 2 17.8311 2 16.7V5.43518C2 4.30402 2.89642 3.38721 3.99433 3.51127Z" stroke="#910024" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <svg id="type-svg"  xmlns="http://www.w3.org/2000/svg" v-show="!this.coursenameDropped" width="24" height="25" viewBox="0 0 24 25" fill="none">
              <path d="M12 6.55337V20.8025M5 8.75464C6.26578 8.95067 7.67778 9.27657 9 9.78788M5 12.7546C5.63949 12.8537 6.3163 12.9859 7 13.1584M3.99433 3.51127C6.21271 3.76195 9.19313 4.43632 11.3168 5.92445C11.725 6.21045 12.275 6.21045 12.6832 5.92445C14.8069 4.43632 17.7873 3.76195 20.0057 3.51127C21.1036 3.38721 22 4.30402 22 5.43518V16.7C22 17.8311 21.1036 18.7483 20.0057 18.8723C17.7873 19.123 14.8069 19.7974 12.6832 21.2855C12.275 21.5715 11.725 21.5715 11.3168 21.2855C9.19313 19.7974 6.21271 19.123 3.99433 18.8723C2.89642 18.7483 2 17.8311 2 16.7V5.43518C2 4.30402 2.89642 3.38721 3.99433 3.51127Z" stroke="#262626" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <p class="type-title">
              과목
            </p>
            <button class="drop-btn"><i class="drop-btn-container" v-on:click="coursenamebtnclick">
              <svg class="toggle-btn" v-show="this.coursenameDropped" xmlns="http://www.w3.org/2000/svg" width="12" height="8" viewBox="0 0 12 8" fill="none">
                <path d="M1 6.5L5.29289 2.20711C5.68342 1.81658 6.31658 1.81658 6.70711 2.20711L11 6.5" stroke="#910024" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <svg class="toggle-btn" v-show="!this.coursenameDropped" xmlns="http://www.w3.org/2000/svg" width="13" height="7" viewBox="0 0 13 7" fill="none">
                <path d="M11.4521 1L7.15925 5.29289C6.76873 5.68342 6.13557 5.68342 5.74504 5.29289L1.45215 0.999999" stroke="#CDCDCD" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </i></button>
          </div>
          <transition name="slide">
            <ul class="year-filter no-dot" v-if="coursenameDropped">
              <li class="item" v-for="(course, index) in uniqueCourses" :key="index">
                <label :for="'course-student' + index" class="checkbox-label">
                  <input :id="'course-student' + index" type="checkbox" class="checkbox" :value="course.course_name" v-model="selectedCourseNameItemsforStudents" @change="courseNameFilterEventChangeforStudents(semester, $event)">
                  <!-- <p v-if="course.course_name === '기타' || course.course_name === ''" class="label-text">기타</p>
                  <p v-else class="label-text">{{course.course_name}} ({{course.course_id}})</p> -->
                  <p class="label-text">{{course.course_name}}</p> <!-- course_id 제거 버전-->
                </label>
              </li>
            </ul>
          </transition>
          <!-- 과목명 필터 한 개 끝 -->
          <!-- (학생 탭) 분반 필터 한 개 시작 -->
          <div class=types :class="[this.courseIdDropped ? 'types-focused' :'types-unfocused']">

            <svg v-show="this.courseIdDropped" id="type-svg"  xmlns="http://www.w3.org/2000/svg" width="24" height="25" viewBox="0 0 24 25" fill="none">
              <path d="M7 14s-1 0-1-1 1-4 5-4 5 3 5 4-1 1-1 1zm4-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6m-5.784 6A2.24 2.24 0 0 1 5 13c0-1.355.68-2.75 1.936-3.72A6.3 6.3 0 0 0 5 9c-4 0-5 3-5 4s1 1 1 1zM4.5 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5" stroke="#910024" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-show="!this.courseIdDropped" id="type-svg"  xmlns="http://www.w3.org/2000/svg" width="24" height="25" viewBox="0 0 24 25" fill="none">
              <path d="M7 14s-1 0-1-1 1-4 5-4 5 3 5 4-1 1-1 1zm4-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6m-5.784 6A2.24 2.24 0 0 1 5 13c0-1.355.68-2.75 1.936-3.72A6.3 6.3 0 0 0 5 9c-4 0-5 3-5 4s1 1 1 1zM4.5 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5" stroke="#262626" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <p class="type-title">
              분반
            </p>
            <button class="drop-btn"><i class="drop-btn-container" v-on:click="courseIdbtnclick">
              <svg class="toggle-btn" v-show="this.courseIdDropped" xmlns="http://www.w3.org/2000/svg" width="12" height="8" viewBox="0 0 12 8" fill="none">
                <path d="M1 6.5L5.29289 2.20711C5.68342 1.81658 6.31658 1.81658 6.70711 2.20711L11 6.5" stroke="#910024" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <svg class="toggle-btn" v-show="!this.courseIdDropped" xmlns="http://www.w3.org/2000/svg" width="13" height="7" viewBox="0 0 13 7" fill="none">
                <path d="M11.4521 1L7.15925 5.29289C6.76873 5.68342 6.13557 5.68342 5.74504 5.29289L1.45215 0.999999" stroke="#CDCDCD" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </i></button>
          </div>
          <transition name="slide">
            <ul class="year-filter no-dot" v-if="courseIdDropped">
              <li class="item" v-for="(course_id, index) in uniqueCourseIDs" :key="index">
                <label :for="'course_id' + index" class="checkbox-label">
                  <input :id="'course_id' + index" type="checkbox" class="checkbox" :value="course_id" v-model="selectedCourseIDItemsforStudents" @change="courseIDFilterEventChangeforStudents(course_id, $event)">
                  <p v-if="course_id === '-1' || course_id === ''" class="label-text">기타</p>
                  <p v-else class="label-text">{{course_id}}</p>
                  <!-- <p class="label-text">{{course_id}}</p> -->
                </label>
              </li>
            </ul>
          </transition>
           <!-- 분반 필터 한 개 끝 -->
        </div>
      </div>
      <!-- student filter 끝 -->
    </div>
    <div class="right-split">
      <div class="title">
        {{titles}}
      </div>
      <InformationCourse v-show="$route.path === '/info/course'" :postss="courseFilteredPosts"></InformationCourse>
      <InformationStudent v-show="$route.path === '/info/students'" :postss="studentsFilteredPosts"></InformationStudent>
      <InformationRepos v-show="$route.path === '/info/repos'" :postss="repoPosts"></InformationRepos>
    </div>
  </div> 
</template>

<script>
import {getCourseInfo, getRepoInfo, getCourseReadDB} from '@/api.js'
import InformationCourse from '@/views/InformationComponents/InformationCourse.vue'
import InformationRepos from '@/views/InformationComponents/InformationRepos.vue'
import InformationStudent from '@/views/InformationComponents/InformationStudent.vue'
export default {
  name: 'Information',
  components: {
    InformationCourse,
    InformationRepos,
    InformationStudent
  },
  data() {
    return {
      titles: '',
      yearDropped: false,
      semesterDropped: false,
      coursenameDropped: false,
      courseIdDropped: false,

      // course data
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

      // student data
      studentsPosts: [],
      studentsFilteredPosts: [],
      studentsFilteredPostsforYear: [],
      studentsFilteredPostsforSemester: [],
      studentsFilteredPostsforCourseName: [],
      studentsFilterYearsCheckbox: [],
      studentsFilterSemesterCheckbox: [],
      studentsFilterCourseNameCheckbox: [],
      studentsFilterCourseIDCheckbox: [],
      selectedYearItemsforStudents: [],
      selectedSemesterItemsforStudents: [],
      selectedCourseNameItemsforStudents: [],
      selectedCourseIDItemsforStudents: [],

      // repository data
      repoPosts: [],
      repoFilteredPosts: [],
    };
  },
  mounted() {
    // this.setInit()
  },
  created() {
    this.setInit()
  },
  computed: {
    isVisible() {

    }
  },
  methods: {
    getRouteType () {
      if (this.$route.name === 'InformationCourse') {
        return 1
      }
      if (this.$route.name === 'InformationStudent') {
        return 2
      }
      if (this.$route.name === 'InformationRepos') {
        return 3
      }
    },
    async currentPost() {
      console.log('helelell')
      console.log(this.coursePosts)
      switch (this.$route.path) {
        case '/info/course':
          return this.coursePosts;
        case '/info/students':
          return this.studentsFilteredPosts;
        case '/info/repos':
          return this.coursePosts;
        default:
          return false;
      }
    },
    async setInit() {
      if(this.$route.name === "InformationCourse") {
        this.titles = '과목 정보'
      }
      if (this.coursePosts.length === 0) {
        await getCourseReadDB().then(res => {
          this.coursePosts = res.data
          this.coursePosts = this.coursePreprocessingTableData(this.coursePosts)
          this.courseFilteredPosts = this.coursePosts
          this.courseFiltering(this.coursePosts)
          this.courseFilteredPostsforYear = this.coursePosts
          this.courseFilteredPostsforSemester = this.coursePosts
          this.courseFilteredPostsforCourseName = this.coursePosts
          this.courseFilteredPostsforCourseID = this.coursePosts
          this.coursePosts = this.yearSort(this.coursePosts)
        })
      }
      if(this.$route.name === "InformationStudent") {
        this.titles = '학생 정보'
      }
      if (this.studentsPosts.length === 0) {
        await getCourseInfo().then(res => {
          this.studentsPosts = res.data
          this.studentsPosts = this.studentsPreprocessingTableData(this.studentsPosts)
          this.studentsPosts = this.yearandCommitSort(this.studentsPosts)
          this.studentsFilteredPosts = this.studentsPosts
          this.studentsFiltering(this.studentsPosts)
          this.studentsFilteredPostsforYear = this.studentsPosts
          this.studentsFilteredPostsforSemester = this.studentsPosts
          this.studentsFilteredPostsforCourseName = this.studentsPosts
          this.studentsFilteredPostsforCourseID = this.studentsPosts
        })
      }
      if(this.$route.name === "InformationRepos") {
        this.titles = '레포지토리 정보'
      }
      // this.repoPosts.length !== 0 조건 없으면 다른 페이지 갔다와야 데이터 로딩됨
      if(this.repoPosts.length === 0 || this.repoPosts.length !== 0 ) {
        getRepoInfo().then(res => {
          this.repoPosts = res.data
          this.repoPosts = this.repoPreprocessingTableData(this.repoPosts)
          this.repoFilteredPosts = this.repoPosts
        })
      }
    },
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
    courseFiltering(courses) {
      const yearset = new Set(courses.map(row => row.year));
      let yearArray = [...yearset];
      let etcYears = yearArray.filter(year => year === '-1' || year === ''); // 기타 항목
      let sortedYears = yearArray.filter(year => year !== '-1' && year !== '').sort((a, b) => a - b); // 숫자 오름차순 정렬
      this.courseFilterYearsCheckbox = [...sortedYears, ...etcYears]; // 정렬된 배열과 기타 항목 결합

      const semesterset = new Set(courses.map(row => row.semester));
      let semesterArray = [...semesterset];
      let etcSemesters = semesterArray.filter(semester => semester === '-1' || semester === ''); // 기타 항목
      let sortedSemesters = semesterArray.filter(semester => semester !== '-1' && semester !== '').sort((a, b) => a - b); // 숫자 오름차순 정렬
      this.courseFilterSemesterCheckbox = [...sortedSemesters, ...etcSemesters]; // 정렬된 배열과 기타 항목 결합

      const courseIDset = new Set(courses.map(row => row.course_id));
      let courseIDArray = [...courseIDset];
      let etcCourseIDs = courseIDArray.filter(id => id === '-1' || id === ''); // 기타 항목
      let sortedCourseIDs = courseIDArray.filter(id => id !== '-1' && id !== '').sort((a, b) => a.localeCompare(b, 'ko', { numeric: true, sensitivity: 'base' })); // 문자 오름차순 정렬
      this.courseFilterCourseIDCheckbox = [...sortedCourseIDs, ...etcCourseIDs]; // 정렬된 배열과 기타 항목 결합

      // const courseset = new Set(courses.map(row=>row.course_name));
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
    
    studentsFiltering(students) {
      const yearset = new Set(students.map(row=>row.year));
      this.studentsFilterYearsCheckbox = [...yearset];

      const semesterset = new Set(students.map(row=>row.semester));
      this.studentsFilterSemesterCheckbox = [...semesterset];

      const courseIDset = new Set(students.map(row=>row.course_id));
      this.studentsFilterCourseIDCheckbox = [...courseIDset];

      // const courseset = new Set(students.map(row=>row.course_name));
      // course id도 추가
      const courseMap = new Map();
      students.forEach(student => {
        if (!courseMap.has(student.course_id)) {
          courseMap.set(student.course_id, {
            course_name: student.course_name,
            course_id: student.course_id
          });
        }
      });
      // 정렬 기능 추가
      this.studentsFilterCourseNameCheckbox = Array.from(courseMap.values()).sort((a, b) => {
        return a.course_name.localeCompare(b.course_name, 'ko', { numeric: true, sensitivity: 'base' });
      });
    },
    coursePreprocessingTableData(datalist) {
      var li = []
      datalist.forEach(element => {
          var newData = new Object()
          if(element.year === '' || !element.year) {
            newData.year = '-1'
          } else {
            newData.year = element.year
          }
          newData.semester = element.semester
          newData.yearandsemester = element.year + '-' + element.semester
          newData.course_name = element.name
          newData.course_id = element.course_id
          newData.prof = element.prof
          newData.students = element.student_count
          newData.commit = element.total_commits
          newData.pr = element.total_prs
          newData.issue = element.total_issues
          newData.stars = element.total_stars
          newData.num_repos = element.repository_count
          li.push(newData)
      });
      return li;
    },
    studentsPreprocessingTableData(datalist) {
      var li = []
      datalist.forEach(element => {
          var newData = new Object()
          if(element.year === '' || !element.year) {
            newData.year = '-1'
          } else {
            newData.year = element.year
          }
          newData.id = element.id
          newData.github = element.github_id
          newData.name = element.name
          newData.semester = element.semester
          newData.department = element.department
          newData.enrollment = element.enrollment
          newData.yearandsemester = element.year + '-' + element.semester
          newData.course_name = element.course_name
          newData.course_id = element.course_id
          newData.prof = element.prof
          newData.commit = element.commit
          newData.pr = element.pr
          newData.issue = element.issue
          newData.num_repos = element.num_repos
          li.push(newData)
      });
      return li;
    },
    // 이 코드 있으니까 다른 페이지에서 레포지토리로 이동 시, commit 등의 데이터를 출력하지 못함.
    repoPreprocessingTableData(datalist) {
      var li = []
      datalist.forEach(element => {
          var newData = new Object()
          // if(element.year === '' || !element.year) {
          //   newData.year = '-1'
          // } else {
          //   newData.year = element.year
          // }
          newData.id = element.id
          newData.owner_github_id = element.owner_github_id
          newData.name = element.name
          newData.commit_count = element.commit_count
          newData.pr_count = element.pr_count
          newData.total_issue_count = element.total_issue_count
          newData.fork_count = element.fork_count
          newData.star_count = element.star_count
          newData.language = element.language
          newData.contributors = element.contributors
          newData.url = element.url
          newData.contributors_list = element.contributors_list;
          li.push(newData)
      });
      console.log('done')
      return li;
    },
    yearSort(li){
      li.sort(function(a,b){
        if( !a.year ) {
          a.year = -1
        }
        if(!b.year) {
          b.year = -1
        }
        return b.year - a.year
      });
      return li
    },
    yearandCommitSort(li) {
      li.sort(function(a, b) {
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
    combineFilterDataforCourse() {
      const allData = [this.courseFilteredPostsforYear, this.courseFilteredPostsforSemester, this.courseFilteredPostsforCourseName, this.courseFilteredPostsforCourseID];
      if (allData.length === 0) return this.coursePosts;

      let common = allData[0];
      
      for (let i = 1; i < allData.length; i++) {
        common = common.filter(item1 => 
          allData[i].some(item2 => item1.year === item2.year && item1.semester === item2.semester && item1.course_id === item2.course_id)
        );
      }
      return common;
    },
    combineFilterDataforStudents() {
      const allData = [this.studentsFilteredPostsforYear, this.studentsFilteredPostsforSemester, this.studentsFilteredPostsforCourseName, this.studentsFilteredPostsforCourseID];
      if (allData.length === 0) return this.studentsPosts;

      let common = allData[0];
      
      for (let i = 1; i < allData.length; i++) {
        common = common.filter(item1 => 
          allData[i].some(item2 => item1.year === item2.year && item1.semester === item2.semester && item1.course_id === item2.course_id)
        );
      }
      return common;
    },
    yearFilterEventChangeforCourse(item, event) {
      if(this.selectedYearItemsforCourse.length === 0) {
        this.courseFilteredPostsforYear = this.coursePosts
      } else {
        this.courseFilteredPostsforYear = this.coursePosts.filter(item => this.selectedYearItemsforCourse.includes(item.year));
      }
      this.courseFilteredPosts = this.combineFilterDataforCourse()
    },
    yearFilterEventChangeforStudents(item, event) {
      if(this.selectedYearItemsforStudents.length === 0) {
        this.studentsFilteredPostsforYear = this.studentsPosts
      } else {
        this.studentsFilteredPostsforYear = this.studentsPosts.filter(item => this.selectedYearItemsforStudents.includes(item.year));
      }
      this.studentsFilteredPosts = this.combineFilterDataforStudents()
    },
    semesterFilterEventChangeforCourse(item, event) {
      if(this.selectedSemesterItemsforCourse.length === 0) {
        this.courseFilteredPostsforSemester = this.coursePosts
      } else {
        this.courseFilteredPostsforSemester = this.coursePosts.filter(item => this.selectedSemesterItemsforCourse.includes(item.semester));
      }
      this.courseFilteredPosts = this.combineFilterDataforCourse()
    },
    semesterFilterEventChangeforStudents(item, event) {
      if(this.selectedSemesterItemsforStudents.length === 0) {
        this.studentsFilteredPostsforSemester = this.studentsPosts
      } else {
        this.studentsFilteredPostsforSemester = this.studentsPosts.filter(item => this.selectedSemesterItemsforStudents.includes(item.semester));
      }
      this.studentsFilteredPosts = this.combineFilterDataforStudents()
    },
    courseNameFilterEventChangeforCourse(item, event) {
      if(this.selectedCourseNameItemsforCourse.length === 0) {
        this.courseFilteredPostsforCourseName = this.coursePosts
      } else {
        this.courseFilteredPostsforCourseName = this.coursePosts.filter(item => this.selectedCourseNameItemsforCourse.includes(item.course_name));
      }
      this.courseFilteredPosts = this.combineFilterDataforCourse()
    },
    courseNameFilterEventChangeforStudents(item, event) {
      if(this.selectedCourseNameItemsforStudents.length === 0) {
        this.studentsFilteredPostsforCourseName = this.coursePosts
      } else {
        this.studentsFilteredPostsforCourseName = this.coursePosts.filter(item => this.selectedCourseNameItemsforStudents.includes(item.course_name));
      }
      this.studentsFilteredPosts = this.combineFilterDataforStudents()
    },
    courseIDFilterEventChangeforCourse(item, event) {
      if (this.selectedCourseIDItemsforCourse.length === 0) {
        this.courseFilteredPostsforCourseID = this.coursePosts;
      } else {
        this.courseFilteredPostsforCourseID = this.coursePosts.filter(item => {
          // 선택된 마지막 두 자리 값과 원래 course_id의 마지막 두 자리를 비교하여 필터링
          const lastTwoDigits = item.course_id.split('-').pop(); // 현재 item의 course_id의 마지막 두 자리
          return this.selectedCourseIDItemsforCourse.includes(lastTwoDigits);
        });
      }
      this.courseFilteredPosts = this.combineFilterDataforCourse();
    },
    courseIDFilterEventChangeforStudents(item, event) {
      if(this.selectedCourseIDItemsforStudents.length === 0) {
        this.studentsFilteredPostsforCourseID = this.coursePosts
      } else {
        this.studentsFilteredPostsforCourseID = this.coursePosts.filter(item => {
          // 선택된 마지막 두 자리 값과 원래 course_id의 마지막 두 자리를 비교하여 필터링
          const lastTwoDigits = item.course_id.split('-').pop(); // 현재 item의 course_id의 마지막 두 자리
          return this.selectedCourseIDItemsforStudents.includes(lastTwoDigits);
        });
      }
      this.studentsFilteredPosts = this.combineFilterDataforStudents()
    },
    resetFilterforCourse() {
      this.selectedYearItemsforCourse = []
      this.selectedSemesterItemsforCourse = []
      this.selectedCourseNameItemsforCourse = []
      this.selectedCourseIDItemsforCourse = []
      this.courseFilteredPostsforYear = this.coursePosts
      this.courseFilteredPostsforSemester = this.coursePosts
      this.courseFilteredPostsforCourseName = this.coursePosts
      this.courseFilteredPostsforCourseID = this.coursePosts
      this.courseFilteredPosts = this.coursePosts
    },
    resetFilterforStudents() {
      this.selectedYearItemsforStudents = []
      this.selectedSemesterItemsforStudents = []
      this.selectedCourseNameItemsforStudents = []
      this.selectedCourseIDItemsforStudents = []
      this.studentsFilteredPostsforYear = this.studentsPosts
      this.studentsFilteredPostsforSemester = this.studentsPosts
      this.studentsFilteredPostsforCourseName = this.studentsPosts
      this.studentsFilteredPostsforCourseID = this.studentsPosts
      this.studentsFilteredPosts = this.studentsPosts
    }
  },
  computed: {
    uniqueCourses() {
    // 과목 이름을 기준으로 중복된 항목을 제거
    const seen = new Set();
    return this.studentsFilterCourseNameCheckbox.filter(course => {
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
    if(this.$route.fullPath === "/info") {
      this.$router.replace('/info/course')
    }
  },
  watch: {
    $route(to, from) {
      if (to.path !== from.path) {
        this.setInit()
      }
    }
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
  height: 100vh;
  background: #FFF;
  overflow: hidden; /* Ensure no overflow issues */
}


.left-split {
  margin-left: 320px;
  width: 268px !important;
  min-width: 268px;
  height: 100vh;
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
    .filter-container{
      /* margin-top:20px; */
      width: 268px;
      height: 100em;
      /* border-left: solid 1px black; */
      border-right: 2px solid;
      border-right-color: #DCE2ED;
      .types{
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
          color:#910024;
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
  height: 100vh;
  .title {
    font-size: 28px;
    font-weight: 700;
    margin-top: 57px;
    margin-left: 57px;
    height:33px;
    min-height: 33px;
    margin-bottom: 34px;
  }
}
.no_dot {
  list-style-type: none;
  list-style: none;
}
ul {
  list-style:none;
  padding-left:0px;
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
    .toggle-btn {

    }
  }
}

.year-filter {
  transform-origin: top;
  transition: transform .2s ease-in-out;
  overflow: hidden;
  background: var(--Primary_background, #FFFBFB);
}
.slide-enter {
    transition: transform .0s ease-in-out;
}
.slide-enter-active, .slide-leave-to{
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
  background-color: #910024; /* 원하는 색상으로 변경 */
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
