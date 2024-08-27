<template>
  <div class="container">
    <div class="navigation">
      <div class="menu">
        <router-link v-bind:to="'/info/course'" class="default-router plan-text" append>과목</router-link>
      </div>
      <div class="menu">
        <router-link v-bind:to="'/info/students'" class="default-router plan-text" append>학생</router-link>
      </div>
      <div class="menu">
        <div class="default-router plan-text current-tab">레포지토리</div>
      </div>
      <div class="search-box">
      <div class="form__group field">
        <input type="input" class="form-field" :value="searchField" />
        <label class="form__label">SEARCH</label>
      </div>
      </div>
    </div>
    <div class="navigation_underline"></div>
    <div class="contents-box">
      <div class="table">
        <table class="table-over" style="table-layout: fixed"> 
          <thead class="table-header-wrapper">
            <th class="table-header" v-for="item in header" v-bind:style="{width: tablewidth(item[1])}">{{item[0]}}</th>
          </thead>
          <tbody>
            <tr v-for="item in sclicedPosts" :key="item.id" class="table-row">
              <td :title="item.name">{{item.name}}</td>
              <td>{{item.star_count}}</td>
              <td>{{item.fork_count}}</td>
              <td>{{item.commit_count}}</td>
              <td>{{item.pr_count}}</td>
              <td>{{item.total_issue_count}}</td>
              <td :title="item.language">{{item.language}}</td>
              <td>{{item.contributors}}</td>
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
                :class="{ active: page === currentPage }"
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
import {getRepoInfo, postCourseUpload} from '@/api.js'
import * as XLSX from 'xlsx';
export default {
  name: 'StatisticsRepo',
  props: ["postss"],
  data() {
    return {
      showOverlay: false,
      showTable: false,
      searchField: '',
      pannelLoading: false,
      posts: [],
      sclicedPosts: [],
      currentPage: 1,
      postsPerPage: 10,
      header : [
        ['레포지토리', '20%'],
        ['스타 수', '10%'], 
        ['포크 수', '10%'], 
        ['커밋 수', '10%'], 
        ['PR 수', '10%'], 
        ['이슈 수', '10%'], 
        ['언어', '20%'], 
        ['기여자 수', '10%']
      ],
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
      return Math.floor((this.currentPage - 1) / 10) === 0
    },
    nextPageDisabledforAll() {
      return Math.floor((this.currentPage - 1) / 10) + 1 >= this.totalPagesPerListforAll
    },
    firstPageDisabledforAll() {
      return this.currentPage === 1
    },
    lastPageDisabledforAll() {
      return this.currentPage === this.totalPagesforAll
    },
    pagesToShowforAll() {
      const startPage = Math.floor((this.currentPage - 1) / 10) * 10 + 1;
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
      this.currentPage = toPage;
    },
    firstPageforAll() {
      if (this.currentPage > 1) {
        this.changePageforAll(1);
      }
    },
    prevPageforAll() {
      if (this.currentPage > 1) {
      this.changePageforAll(this.currentPage - 1);
      }
    },
    nextPageforAll() {
      if (this.currentPage < this.totalPagesforAll) {
      this.changePageforAll(this.currentPage + 1);
      }
    },
    lastPageforAll() {
      if (this.currentPage < this.totalPagesforAll) {
        this.changePageforAll(this.totalPagesforAll);
      }
    },
    toggle() {
      this.showTable = !this.showTable;
    },
    tablewidth(length) {
      return length;
    },
    slicingforall() {
      const start = (this.currentPage - 1) * this.postsPerPage;
      const end = start + this.postsPerPage;
      this.sclicedPosts = this.yearandCommitSort(this.posts.slice(start, end));
    },
    commitSort(li){
      li.sort(function(a,b){
        if( !a.commit_count ) {
          a.commit_count = 0
      }
        if(!b.commit_count) {
          b.commit_count = 0
        }
        return b.commit_count - a.commit_count
      });
      return li
    },
    yearandCommitSort(li) {
      li.sort(function(a, b) {
        return b.commit_count - a.commit_count;
      });
      return li;
    },
    toSummarized(li) {
      var ret = []
      const ids = new Set(li.map(row=>row.id));
      const uniqueArr  = [...ids];
      li.forEach(element => {
        let index = uniqueArr.indexOf(element.id)

        if (ret[index] === undefined) {
          var newData = new Object()
          newData.id = element.id
          newData.name = element.name
          newData.owner_github_id = element.owner_github_id
          newData.commit_count = element.commit_count
          newData.pr_count = element.pr_count
          newData.total_issue_count = element.total_issue_count
          newData.fork_count = element.fork_count
          newData.star_count = element.star_count
          ret[index] = newData
        }
        else {
          var appendData = ret[index]
          appendData.commit_count = appendData.commit_count + element.commit_count
          appendData.pr_count = appendData.pr_count + element.pr_count
          appendData.total_issue_count = appendData.total_issue_count + element.total_issue_count
          appendData.fork_count = appendData.fork_count + element.fork_count
          appendData.star_count = appendData.star_count + element.star_count
          ret[index] = appendData   
        }
      });
      ret = this.commitSort(ret)
      return ret
    },
    changeRoutebyTable() {
      if (this.showTable) {
        this.$router.replace({ path: this.$route.path, query: { page: 1, type: 'summary' } });
      } else if (!this.showTable) {
        this.$router.replace({ path: this.$route.path, query: { page: 1, type: 'all' } });
      }
      this.slicingforall();
      this.toSummarized(this.posts);
      this.slicingforsummary();
    },
  },
  mounted() {
    this.currentPage = parseInt(this.$route.query.page) || 1;
    this.slicingforall();
    this.toSummarized(this.posts);
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
    this.currentPage = parseInt(query.page) || 1;
  },
  watch: {
    postss(to, from) {
      this.posts = to;
      console.log(this.posts)
      this.slicingforall();
      if (this.$route.query.page > this.totalPagesforAll) {
        this.changePageforAll(this.totalPagesforAll);
      }
      this.toSummarized(this.posts);
    },
    $route(to, from) {
      console.log(this.posts)
      this.currentPage = parseInt(to.query.page) || 1;
      this.slicingforall();
    },
    currentPage(to, from) {
      this.slicingforall();
      this.toSummarized(this.posts);

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
  .search-box {
    min-height: 44px;
    margin-left: auto;
    margin-right: 60px;
    align-self: flex-end;
    padding-bottom: 4px;
    margin-right: 26px;

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
