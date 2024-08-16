<template>
  <div class="container" :class="{cursorblock: pannelLoading === true}">
    <div class="import-overlay" v-show="this.showOverlay" v-on:click="changeOverlay">
      <div class="pannel-container" :class="{pannelblock : pannelLoading === true}" @click.stop >
        <pulse-loader class="loader" :loading="pannelLoading" v-bind:color="'#910024'" :size="'15px'"></pulse-loader>
        <div class="pannel-top">
          <div class="text">Import Course</div>
          <div class="exit-svg" v-on:click="changeOverlay">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path fill-rule="evenodd" clip-rule="evenodd" d="M11.9498 13.364C12.3403 13.7545 12.9734 13.7545 13.364 13.364C13.7545 12.9734 13.7545 12.3403 13.364 11.9497L8.41424 7.00002L13.364 2.05031C13.7545 1.65978 13.7545 1.02662 13.364 0.636092C12.9734 0.245567 12.3403 0.245567 11.9497 0.636092L7.00003 5.5858L2.05026 0.636033C1.65973 0.245508 1.02657 0.245509 0.636045 0.636033C0.24552 1.02656 0.24552 1.65972 0.636045 2.05025L5.58582 7.00002L0.636033 11.9498C0.245508 12.3403 0.245509 12.9735 0.636033 13.364C1.02656 13.7545 1.65972 13.7545 2.05025 13.364L7.00003 8.41423L11.9498 13.364Z" fill="#262626"/>
            </svg>
          </div>
        </div>
        <div class="pannel-body">
          <div class="import-container">
            <input class="input-for-import" v-model="importItem.course_id" @focus="clearErrorMessageforCourseID" type="text" id="course_id" placeholder="학수번호" required>
            </input>
            <p class="err-msg">{{this.ValidationItem.course_id}}</p>
          </div>
          <div class="import-container">
            <input class="input-for-import" v-model="importItem.year" @focus="clearErrorMessageforYear" type="text" id="year" placeholder="연도" required>
            </input>
            <p class="err-msg">{{this.ValidationItem.year}}</p>
          </div>
          <div class="import-container">
            <input class="input-for-import" v-model="importItem.semester" @focus="clearErrorMessageforSemester" type="text" id="semester" placeholder="학기" required>
            </input>
            <p class="err-msg">{{this.ValidationItem.semester}}</p>
          </div>
          <div class="import-container">
            <input class="input-for-import" v-model="importItem.course_name" @focus="clearErrorMessageforCourseName" type="text" id="course_name" placeholder="과목명" required>
            </input>
            <p class="err-msg">{{this.ValidationItem.course_name}}</p>
          </div>
          <div class="import-container">
            <input class="input-for-import" v-model="importItem.prof" @focus="clearErrorMessageforProf" type="text" id="prof" placeholder="교수" required>
            </input>
            <p class="err-msg">{{this.ValidationItem.prof}}</p>
          </div>
          <div class="import-container">
            <input class="input-for-import" v-model="importItem.ta" @focus="clearErrorMessageforTA" type="text" id="ta" placeholder="조교" required>
            </input>
            <p class="err-msg">{{this.ValidationItem.ta}}</p>
          </div>
          <div class="import-container">
            <label for="file">
              <div class="btn-upload">
                <div class="svg">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M12 8V16M16 12H8M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="#616161" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
                <div class="text">교과목 학생 파일</div>
              </div>
            </label>
            <p class="err-msg">{{this.ValidationItem.file}}</p>
            <input type="file" name="file" id="file" v-on:change="selectFile" accept=".xlsx, xls, .csv" />
          </div>
          <div class="import-container">
            <p class="uploaded-file">Selected File Name</p>
            <p v-show="this.selectedFile" class="uploaded-file-name">{{this.selectedFileName}}</p>
          </div>
        </div>
        <div class="pannel-footer">
          <div class="cancel-btn" v-on:click="closeImportDialog"> 취소 </div>
          <div class="accept-btn" v-on:click="fileUpload"> 확인 </div>
        </div>
      </div>
    </div>
    <div class="navigation">
      <div class="menu">
        <div class="default-router plan-text current-tab">과목</div>
      </div>
      <div class="menu">
        <router-link v-bind:to="'/info/students'" class="default-router plan-text" append>학생</router-link>
      </div>
      <div class="menu">
        <router-link v-bind:to="'/info/repos'" class="default-router plan-text" append>레포지토리</router-link>
      </div>
      <div class="search-box">
        <div class="form__group field">
          <input type="input" class="form-field" :value="searchField" />
          <label class="form__label">SEARCH</label>
        </div>
      </div>
      <div class="import-btn" v-on:click="changeOverlay">
        <div class="import-btn-svg">
          <svg id="svg-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="18" viewBox="0 0 20 18" fill="none">
            <path d="M4.75 0.25C2.12665 0.25 0 2.37665 0 5V13C0 15.6234 2.12665 17.75 4.75 17.75H12C14.6234 17.75 16.75 15.6234 16.75 13C16.75 12.5858 16.4142 12.25 16 12.25C15.5858 12.25 15.25 12.5858 15.25 13C15.25 14.7949 13.7949 16.25 12 16.25H7.46412C8.26157 15.4003 8.75 14.2572 8.75 13V5C8.75 3.74279 8.26157 2.59965 7.46412 1.75H12C13.7949 1.75 15.25 3.20507 15.25 5C15.25 5.41421 15.5858 5.75 16 5.75C16.4142 5.75 16.75 5.41421 16.75 5C16.75 2.37665 14.6234 0.25 12 0.25H4.75Z" fill="#CB385C"/>
            <path d="M13.5302 6.46967C13.8231 6.76256 13.8231 7.23744 13.5302 7.53033L12.8105 8.25L19.2499 8.25C19.6641 8.25 19.9999 8.58579 19.9999 9C19.9999 9.41421 19.6641 9.75 19.2499 9.75L12.8105 9.75L13.5302 10.4697C13.8231 10.7626 13.8231 11.2374 13.5302 11.5303C13.2373 11.8232 12.7624 11.8232 12.4695 11.5303L11.1766 10.2374C10.4932 9.55402 10.4932 8.44598 11.1766 7.76256L12.4695 6.46967C12.7624 6.17678 13.2373 6.17678 13.5302 6.46967Z" fill="#CB385C"/>
          </svg>
          <div class="import-btn-svg-text">Import</div>
        </div>
      </div>
    </div>
    <div class="navigation_underline"></div>
    <div class="contents-box">
      <div class="table">
        <table class="table-over" style="table-layout: fixed"> 
          <thead class="table-header-wrapper"><th class="table-header" v-for="item in header" v-bind:style="{width: tablewidth(item[1])}">{{item[0]}}</th></thead>
          <tbody>
            <tr v-for="item in posts" class="table-row">
              <!-- {{item}} -->
              <td>{{item.yearandsemester}}</td>
              <td>{{item.course_name}}</td>
              <td>{{item.course_id}}</td>
              <td>{{item.prof}}</td>
              <td>{{item.students}}</td>
              <td>{{item.commit}}</td>
              <td>{{item.pr}}</td>
              <td>{{item.issue}}</td>
              <td>{{item.num_repos}}</td>
            </tr>
          </tbody>
        </table>
        <div class="pagenation-container">
          <div class="pagenation-wrapper">
            <button @click="firstPageforAll" :disabled="firstPageDisabledforAll" class="prev-button">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path class="prev-pointer" d="M15 18L9 12L15 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path class="prev-pointer" d="M19 18L13 12L19 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <button @click="prevPageforAll" :disabled="prevPageDisabledforAll" class="prev-button">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path class="prev-pointer" d="M15 18L9 12L15 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <button
              v-for="page in pagesToShowforAll"
              :key="page"
              @click="changePageforAll(page)"
              :class="{ active: page === currentPageforAll }"
              class="number-list-btn">
              {{ page }}
            </button>
            <button @click="nextPageforAll" :disabled="nextPageDisabledforAll" class="next-button">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path class="next-pointer" d="M9 18L15 12L9 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <button @click="lastPageforAll" :disabled="lastPageDisabledforAll" class="next-button">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path class="next-pointer" d="M9 18L15 12L9 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path class="next-pointer" d="M5 18L11 12L5 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {getCourseInfo, postCourseUpload} from '@/api.js'
import * as XLSX from 'xlsx';
export default {
  name: 'StatisticsTotal',
  props: ["postss"],
  data() {
    return {
      showOverlay: false,
      showTable: false,
      searchField: '',
      selectedFile: null,
      pannelLoading: false,
      posts: [],
      sclicedPosts: [],
      currentPage: 1,
      postsPerPage: 10,
      header : [['개설학기', '9%'], 
                ['과목명', '14%'], 
                ['학수번호', '11%'], 
                ['지도교수', '11%'], 
                ['수강생', '11%'],
                ['Commit', '11%'], 
                ['PR', '11%'], 
                ['Issue', '11%'], 
                ['Repos', '11%']],
      importItem: {
        course_id: '',
        year: '',
        semester: '',
        course_name: '',
        prof: '',
        ta: '',
      },
      ValidationItem: {
        course_id: '',
        year: '',
        semester: '',
        course_name: '',
        prof: '',
        ta: '',
        file: '',
      },
      selectedFileName: '',
    };
  },
  computed: {
    totalPagesforAll() {
      return Math.ceil(this.postss.length / this.postsPerPage);
    },
    totalPagesPerListforAll() {
      return  Math.floor(Math.ceil(this.postss.length / this.postsPerPage) / 10) + 1;
    },
    prevPageDisabledforAll() {
      return Math.floor((this.currentPageforAll - 1) / 10) === 0
    },
    nextPageDisabledforAll() {
      return Math.floor((this.currentPageforAll - 1) / 10) + 1 >= this.totalPagesPerListforAll
    },
    firstPageDisabledforAll() {
      return this.currentPageforAll === 1
    },
    lastPageDisabledforAll() {
      return this.currentPageforAll === this.totalPagesforAll
    },
    pagesToShowforAll() {
      const startPage = Math.floor((this.currentPageforAll - 1) / 10) * 10 + 1;
      const endPage = Math.min(startPage + 9, this.totalPagesforAll);
      const pages = [];
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
      return pages;
    },
  },
  methods: {
    changePageforAll(page) {
      let toPage = 0
      if (page < 1) {
        toPage = 1;  
      } else if (page > this.totalPagesforAll) {
        toPage = this.totalPagesforAll;
      } else {
        toPage = page;
      }
      const query = { ...this.$route.query, page: toPage };
      this.$router.replace({ path: this.$route.path, query: query });
      this.currentPageforAll = toPage;
    },
    firstPageforAll() {
      if (this.currentPageforAll > 1) {
        this.changePageforAll(1);
      }
    },
    prevPageforAll() {
      if (this.currentPageforAll > 1) {
        this.changePageforAll(Math.floor((this.currentPageforAll - 1) / 10));
      }
    },
    nextPageforAll() {
      if (Math.floor((this.currentPageforAll - 1) / 10) + 1 < this.totalPagesPerListforAll) {
        this.changePageforAll(Math.floor((this.currentPageforAll - 1) / 10) + 11);
      }
    },
    lastPageforAll() {
      if (this.currentPageforAll < this.totalPagesforAll) {
        this.changePageforAll(this.totalPagesforAll);
      }
    },
    selectFile(e) {
      this.selectedFile = e.target.files[0];
      this.selectedFileName = this.selectedFile.name
      console.log(this.selectedFile)
    },
    toggle() {
      this.showTable = !this.showTable;
    },
    slicingforall() {
      const start = (this.currentPageforAll - 1) * this.postsPerPage;
      const end = start + this.postsPerPage;
      this.sclicedPosts = this.yearandCommitSort(this.posts.slice(start, end));
    },
    checkInput() {
      let onormore = false;
      if(this.importItem.course_id === '') {
        this.ValidationItem.course_id = 'The Course ID is required.'
        onormore = true
      }
      if(this.importItem.year === '') {
        this.ValidationItem.year = 'The Year is required.'
        onormore = true
      }
      if(this.importItem.semester === '') {
        this.ValidationItem.semester = 'The Semester is required.'
        onormore = true
      }
      if(this.importItem.course_name === '') {
        this.ValidationItem.course_name = 'The Course Name is required.'
        onormore = true
      }
      if(this.importItem.prof === '') {
        this.ValidationItem.prof = 'The Professor Name is required.'
        onormore = true
      }
      if(this.importItem.ta === '') {
        this.ValidationItem.ta = 'The TA Name is required.'
        onormore = true
      }
      if(!this.selectedFile) {
        this.ValidationItem.file = 'The TA Name is required.'
        this.selectedFileName = ''
        onormore = true
      } else {
        this.selectedFileName = this.selectedFile.name
      }
      return onormore
    },
    clearErrorMessageforCourseID() {
      this.ValidationItem.course_id = ''
    },
    clearErrorMessageforYear() {
      this.ValidationItem.year = ''
    },
    clearErrorMessageforSemester() {
      this.ValidationItem.semester = ''
    },
    clearErrorMessageforCourseName() {
      this.ValidationItem.course_name = ''
    },
    clearErrorMessageforProf() {
      this.ValidationItem.prof = ''
    },
    clearErrorMessageforTA() {
      this.ValidationItem.ta = ''
    },
    clearErrorMessageforFile() {
      this.ValidationItem.file = ''
      this.selectedFileName = ''
    },
    clearAllMessages() {
      this.clearErrorMessageforCourseID()
      this.clearErrorMessageforYear()
      this.clearErrorMessageforSemester()
      this.clearErrorMessageforCourseName()
      this.clearErrorMessageforProf()
      this.clearErrorMessageforTA()
      this.clearErrorMessageforFile()
    },
    changeOverlay() {
      this.showOverlay = !this.showOverlay
    },
    tablewidth(length) {
      return length
    },
    fileUpload() {
      if (this.checkInput()) {
        return;
      }
      this.pannelLoading = true
      const reader = new FileReader();
      
      reader.onload = async (e) => {
        console.log(e)
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
        const sheetData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });
        const importDetails = [
          this.importItem.course_id,
          this.importItem.year,
          this.importItem.semester,
          this.importItem.course_name,
          this.importItem.prof,
          this.importItem.ta,
        ];
        sheetData.unshift(importDetails);

        // Convert back to worksheet and workbook
        const newWorksheet = XLSX.utils.aoa_to_sheet(sheetData);
        const newWorkbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(newWorkbook, newWorksheet, 'Sheet1');

        // Write the new workbook to a blob
        const newExcelBuffer = XLSX.write(newWorkbook, { bookType: 'xlsx', type: 'array' });
        const newFile = new Blob([newExcelBuffer], { type: 'application/octet-stream' });

        // Prepare the form data for upload
        const formData = new FormData();
        formData.append('file', newFile, 'modified_import.xlsx');
        formData.append('course_id', this.importItem.course_id);
        formData.append('year', this.importItem.year);
        formData.append('semester', this.importItem.semester);
        formData.append('name', this.importItem.course_name);
        formData.append('prof', this.importItem.prof);
        formData.append('ta', this.importItem.ta);
        postCourseUpload(formData).then(response => {
          this.closeImportDialog()
        }).catch(e => {
          console.error('Error Uploading file:', error);
          this.pannelLoading = false
        })
      };
      reader.readAsArrayBuffer(this.selectedFile);
    },
    closeImportDialog() {
      this.showOverlay = false;
      this.clearAllMessages()
      this.selectedFile = null;
      this.pannelLoading = false
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
  },
  mounted() {
    this.posts = this.postss
    this.currentPageforAll = parseInt(this.$route.query.page) || 1;
    this.slicingforall();
  },
  beforeMount() {
    const query = this.$route.query;
    const newQuery = { ...query };
    let needsReplace = false;
    if (!query.page) {
      newQuery.page = 1;
      needsReplace = true;
    }

    if (needsReplace) {
      this.$router.replace({ path: this.$route.path, query: newQuery });
    }
    this.currentPageforAll = parseInt(query.page) || 1;
  },
  watch: {
    postss(to, from) {
      this.posts = to;
      this.slicingforall();
      if (this.$route.query.page > this.totalPagesforAll) {
        this.changePageforAll(this.totalPagesforAll);
      }
    },
    $route(to, from) {
      this.currentPageforAll = parseInt(to.query.page) || 1;
      this.slicingforall();
    },
    currentPageforAll(to, from) {
      this.slicingforall();
    },
  }
};
</script>

<style scoped>
.cursorblock {
  pointer-events: none; 
}
.container {
  max-width: 1600px;

  .navigation {
    min-height: 41px;
    padding-left: 56px;
    padding-right: 56px;
    /* margin-left: 56px; */
    display: flex;
    align-items: center;

    .menu {
      width: 101px;
      margin-right: 30px !important;
      font-size: 18px;
      align-items: center;
      text-align: center;

      .plan-text {
        margin: 0 auto;
        line-height: 41px;
      }

      .current-tab {
        color: #862633 !important;
        border-bottom: solid 4px #862633;
      }
    }
  }
  .contents-box {
    padding: 0 56px;

    .slide-fade-enter-active {
      transition: all 0.3s ease-out;
    }

    .slide-fade-leave-active {
      transition: all 0.2s cubic-bezier(1, 0.5, 0.8, 1);
    }

    .slide-fade-enter-from,
    .slide-fade-leave-to {
      transform: translateX(50px);
      opacity: 0;
    }
  }
  .import-btn {
    min-height: 34px;
    min-width: 117px;
    margin-right: 0;
    padding: 5px 18px;
    
    border-radius: 10px;
    border: 1px solid var(--Primary_medium, #CB385C);
    background: #fff4f5;
    cursor: pointer;
    &:hover {
      background: #ffe9eb;
    }
    .import-btn-svg {
      display: flex;
      align-items: center;
      /* background-color: red; */
      height: 24px;
      #svg-icon {
        /* margin: 0 auto; */
        display: block;
      }
      .import-btn-svg-text {
        display: block;
        margin-left: 8px;
        font-size: 16px;
        font-style: normal;
        font-weight: 500;
        line-height: normal;
        color: var(--Primary_medium, #CB385C);
      }
    }
  }
  .search-box {
    min-height: 44px;
    margin-left: auto;
    margin-right: 60px;
    align-self: flex-end;
    padding-bottom: 4px;

    .form__group {
      position: relative;
      width: 100%;
    }
    
    .form-field {
      font-family: inherit;
      width: 230px;
      height: 40px;
      border: 0;
      border-bottom: 2px solid #9b9b9b;
      outline: 0;
      color: #86263300;
      padding: 1px 0;
      background: transparent;
      transition: border-bottom 0.2s ease-in-out;;
      transition: border-image 0.2s ease-in-out;
      font-size: 1.1rem;
      &::placeholder {
        color: transparent;
      }
    
      &:placeholder-shown ~ .form__label {
        font-size: 18px;
        cursor: text;
      }
    }
    
    .form__label {
      position: absolute;
      top: 5px;
      display: block;
      transition: 0.2s;
      color: #9b9b9b;
      font-size: 1.1rem;
      pointer-events: none;
    }
    
    .form-field:focus {
      ~ .form__label {
        position: absolute;
        top: -25px;
        display: block;
        transition: 0.2s;
        font-size: 1rem;
        color: #CB385C;
        font-weight: 700;
      }
      padding-bottom: 6px;
      font-weight: 700;
      border-width: 3px;
      border-image: linear-gradient(to right, #CB385C, #FFF4F5);
      transition: opacity 1s;
      border-image-slice: 1;
      color: #862633;
    }
    .form-field:focus::before, .form-field:focus::after{
        transition: 0.2s ease-in-out;
    }
    /* reset input */
    .form-field {
      &:required,
      &:invalid {
        box-shadow: none;
      }
    }

  }

}

.navigation_underline {
  border-bottom: solid 2px #dce2ed;
  width: calc(1920px - 586px) !important;
}

.table-over {
  border-collapse: collapse;
  width: 100%;
  font-size: 16px;
  .table-header-wrapper{
    border-top: solid 1px #F9D2D6;
    border-bottom: solid 1px #F9D2D6; 
  }
  .table-header {
    color: var(--Primary_normal, #910024);
    font-weight: 600;
    height: 43px;
    vertical-align: middle;
  }
  .table-row {
    height: 70px;
    border-bottom: solid 1px #DCE2ED;
    text-align: center;
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
    & td {
      text-overflow: ellipsis;
      overflow: hidden;
      white-space: nowrap;
      color: #000000;
    }
  }
}

.table {
  .pagenation-container {
    height: 44px;
    margin-top: 40px;
    display: flex;
    justify-content: center;
    align-items: center;

    .pagenation-wrapper {
      height: 44px;
      display: inline-flex;
      align-items: center;
      
      .btn {
        margin: 0 20px;
      }

      .prev-button, .next-button {
        display: inline-flex;
        align-items: center;
        border: none;
        background: none;
        cursor: pointer;
        height: 44px;
        line-height: 44px;
        /* padding: 0.5rem; */
        margin: 0;
        transition: color 0.3s ease;

        .prev-pointer, .next-pointer {
          width: 44px;
          height: 44px;
          display: inline-block;

          & svg {
            height: 44px;
            display: inline-block;
            vertical-align: middle;
          }
          stroke: #262626;
        }
        &:not(:disabled):hover .prev-pointer {
          stroke: #CB385C;
        }
        &:disabled {
          pointer-events : none;
        }
        &:not(:disabled):hover .next-pointer {
          stroke: #CB385C;
        }
        &:disabled {
          pointer-events : none;
        }
      }
      .number-list-btn {
        height: 44px;
        line-height: 44px;
        margin-left: 10px;
        margin-right: 10px;
        font-size: 16px;
        &:hover {
          color: #CB385C;
        }
      }
      .active {
        font-weight: 700;
        color: #CB385C;
      }
    }
  }
}

.table,
.chart {
  margin: 20px 0;
  padding: 20px 0;
  /* border: 1px solid #dce2ed; */
  border-radius: 4px;
  height: 100%;
  .year-chart-container {
  
    
  }
  .category-chart-container {

  }
  & .title {
    font-size: 22px;
    font-weight: 700;
    
  }
}

.import-overlay {
  position: fixed;
  height: 100vh;
  display: -webkit-box;
  display: -webkit-flex;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -webkit-align-items: center;
  -ms-flex-align: center;
  align-items: center;
  top: 0;
  left: 0;
  height: 100vh;
  width: 100vw;
  background: rgba(0, 0, 0, 0.41);
  z-index: 1000;
  .pannelblock {
    background: #efefef !important;
    pointer-events: none;
  }
  .pannel-container {
    margin: 0 auto;
    width: 710px;
    height: 550px;
    flex-shrink: 0;
    border-radius: 10px;
    background: #FFF;
    transform: rotate(0);
    .loader{
      position: fixed;
      top: 45%;
      left: 45%;
    }
    .pannel-top {
      height: 74px;
      .text {
        display: block;
        height: 24px;
        line-height: 24px;
        font-size: 20px;
        font-style: normal;
        font-weight: 600;
        margin-left: 50px;
        margin-top: 30px;
        float: left;

      }
      .exit-svg {
        display: block;
        margin-left: auto;
        margin-top: 26px;
        margin-right: 50px;
        float: right;
        width: 32px;
        height: 32px;
        line-height: 32px;
        z-index: 1002;
        cursor: pointer;
      }
    }
    .pannel-body {
      display: grid;
      grid-template-columns: repeat(2, 50%);
      /* justify-items: center; */
      margin-top: 30px;
      .import-container {
        width: 280px;
        height: 50px;
        margin-bottom: 40px;
        &:nth-child(odd) {
          margin-left: 50px;
        }
        &:nth-child(even) {
          margin-right: 50px;
          margin-left: auto;
        }
        .input-for-import {
          z-index: 1003;
          display: block;
          /* margin: 0 auto; */
          height: 100%;
          width: 100%;
          border-radius: 10px;
          border: 1px solid var(--Gray100, #CDCDCD);
          background: var(--Gray50, #F8F8F8);
          padding-left: 20px;
          &::placeholder {
            height: 20px;
            /* padding-left: 20px; */
            color: var(--Gray100, #CDCDCD);
            /* text-sm */
            font-family: Pretendard;
            font-size: 16px;
            font-style: normal;
            font-weight: 500;
            line-height: normal;
          }
        }
        .btn-upload {
          width: 183px;
          height: 50px;
          background: #F8F8F8;
          border: 1px solid #616161;
          border-radius: 10px;
          font-weight: 500;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: space-between;
          &:hover {
            border: 1px solid var(--Primary_light, #F9D2D6);
            background: var(--Primary_extralight, #FFEAEC);
            color: var(--Primary_medium, #CB385C);
          }
          .svg {
            width: 24px;
            height: 24px;
            margin-left: 18px;
          }
          .text {
            color: var(--Gray500, #616161);
            font-weight: 500;
            width: 113px;
            font-family: Pretendard;
            font-size: 16px;
            margin-right : 18px;
          }
        }
        #file {
          display: none;
        }
        .err-msg {
          color: red;
          text-align: left;
        }
        .uploaded-file {
          font-weight: 600;
        }
        .uploaded-file-name {
          overflow:hidden;
	        text-overflow:ellipsis;
	        white-space:nowrap;
        }
      }
    }
    .pannel-footer {
      height:70px;
      width: 100%;
      display: flex;
      justify-content: flex-end;
      .cancel-btn {
        display: inline-flex;
        width: 88px;
        height: 40px;
        padding: 10px 20px;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 10px;
        border-radius: 10px;
        background: var(--Gray50, #F8F8F8);
        margin-right: 20px;
        cursor: pointer;
        font-family: Pretendard;
        font-size: 16px;
        font-style: normal;
        font-weight: 500;
        color: var(--Gray500, #616161);
        &:hover {
          background: var(--Gray50, #dadada);
        }
      }
      .accept-btn {
        display: flex;
        width: 172px;
        height: 40px;
        padding: 10px 30px;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 10px;
        flex-shrink: 0;
        border-radius: 10px;
        border: 1px solid var(--Primary_light, #F9D2D6);
        background: var(--Primary_extralight, #FFEAEC);
        cursor: pointer;
        color: var(--Primary_medium, #CB385C);
        /* semiTitle-sm */
        font-family: Pretendard;
        font-size: 16px;
        font-style: normal;
        font-weight: 600;
        margin-right: 50px;

        &:hover {
          background: var(--Primary_extralight, #fcd2d7);
        }
      }
    }
  }
}
</style>
