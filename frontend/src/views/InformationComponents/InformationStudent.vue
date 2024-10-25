<template>
  <div class="container">
    <div class="navigation">
      <div class="menu">
        <router-link v-bind:to="'/info/course'" class="default-router plan-text" append>과목</router-link>
      </div>
      <div class="menu">
        <div class="default-router plan-text current-tab">학생</div>
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
      <div class="toggle-box" @click.self.prevent="toggle">
        <div class="wrapper">
          <input type="checkbox" id="infoswitchstudent" v-model="showTable" @click="changeRoutebyTable">
          <label for="infoswitchstudent" class="switch_label">
            <span class="onf_btn"></span>
            <div class="toggle-text">
              <div class="toggle-total">
                요약
              </div>
              <div class="toggle-indiv">
                전체
              </div>
            </div>
          </label>
        </div>
      </div>
    </div>
    <div class="navigation_underline"></div>
    <div class="contents-box">
      <transition name="slide-fade" mode="out-in">
        <div v-if="!showTable" class="table">
          <table class="table-over" style="table-layout: fixed"> 
            <thead class="table-header-wrapper">
<<<<<<< HEAD
              <th class="table-header" v-for="item in headerforsummary" :key="item[0]" :style="{width: tablewidth(item[1])}">{{item[0]}}</th>
=======
              <!-- 열 제목에 @click 이벤트 추가하여 정렬 가능하도록 설정 -->
              <th class="table-header" @click="sortTable('name')" :style="{width: tablewidth(headerforsummary[0][1])}">
                이름
              </th>
              <th class="table-header" @click="sortTable('department')" :style="{width: tablewidth(headerforsummary[1][1])}">
                학과
              </th>
              <th class="table-header" @click="sortTable('id')" :style="{width: tablewidth(headerforsummary[2][1])}">
                학번
              </th>
              <th class="table-header" @click="sortTable('enrollment')" :style="{width: tablewidth(headerforsummary[3][1])}">
                학적
              </th>
              <th class="table-header" @click="sortTable('github')" :style="{width: tablewidth(headerforsummary[4][1])}">
                Github ID
              </th>
              <th class="table-header" @click="sortTable('commit')" :style="{width: tablewidth(headerforsummary[5][1])}">
                Commit
              </th>
              <th class="table-header" @click="sortTable('pr')" :style="{width: tablewidth(headerforsummary[6][1])}">
                PR
              </th>
              <th class="table-header" @click="sortTable('issue')" :style="{width: tablewidth(headerforsummary[7][1])}">
                Issue
              </th>
              <th class="table-header" @click="sortTable('num_repos')" :style="{width: tablewidth(headerforsummary[8][1])}">
                Repos
              </th>
>>>>>>> origin/dev-jhs
            </thead>
            <tbody>
              <tr v-for="(item, index) in slicedsummarizedStudents" :key="index" class="table-row">
                <td :title="item.name">{{item.name}}</td>
                <td :title="item.department">{{item.department}}</td>
                <td :title="item.id">{{item.id}}</td>
                <td :title="item.enrollment">{{item.enrollment}}</td>
                <td :title="item.github">{{item.github}}</td>
                <td :title="item.commit">{{item.commit}}</td>
                <td :title="item.pr">{{item.pr}}</td>
                <td :title="item.issue">{{item.issue}}</td>
                <td :title="item.num_repos">{{item.num_repos}}</td>
              </tr>
            </tbody>
          </table>
          <div class="pagenation-container">
            <div class="pagenation-wrapper">
              <button @click="firstPageforSummary" :disabled="firstPageDisabledforSummary" class="prev-button">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path class="prev-pointer" d="M15 18L9 12L15 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path class="prev-pointer" d="M19 18L13 12L19 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <button @click="prevPageforSummary" :disabled="prevPageDisabledforSummary" class="prev-button">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path class="prev-pointer" d="M15 18L9 12L15 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <button
                v-for="page in pagesToShowforSummary"
                :key="page"
                @click="changePageforSummary(page)"
                :class="{ active: page === currentPageforSummary }"
                class="number-list-btn">
                {{ page }}
              </button>
              <button @click="nextPageforSummary" :disabled="nextPageDisabledforSummary" class="next-button">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path class="next-pointer" d="M9 18L15 12L9 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <button @click="lastPageforSummary" :disabled="lastPageDisabledforSummary" class="next-button">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path class="next-pointer" d="M9 18L15 12L9 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path class="next-pointer" d="M5 18L11 12L5 6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
        <div v-else class="table">
          <table class="table-over" style="table-layout: fixed"> 
            <thead class="table-header-wrapper">
<<<<<<< HEAD
              <th class="table-header" v-for="item in headerforall" :key="item[0]" :style="{width: tablewidth(item[1])}">{{item[0]}}</th>
=======
              <th class="table-header" @click="sortTableForAll('yearandsemester')" :style="{width: tablewidth(headerforall[0][1])}">
                개설학기
              </th>
              <th class="table-header" @click="sortTableForAll('name')" :style="{width: tablewidth(headerforall[0][1])}">
                이름
              </th>
              <th class="table-header" @click="sortTableForAll('department')" :style="{width: tablewidth(headerforall[1][1])}">
                학과
              </th>
              <th class="table-header" @click="sortTableForAll('id')" :style="{width: tablewidth(headerforall[2][1])}">
                학번
              </th>
              <th class="table-header" @click="sortTableForAll('enrollment')" :style="{width: tablewidth(headerforall[3][1])}">
                학적
              </th>
              <th class="table-header" @click="sortTableForAll('github')" :style="{width: tablewidth(headerforall[4][1])}">
                Github ID
              </th>
              <th class="table-header" @click="sortTableForAll('course_name')" :style="{width: tablewidth(headerforall[5][1])}">
                과목명
              </th>
              <th class="table-header" @click="sortTableForAll('course_id')" :style="{width: tablewidth(headerforall[6][1])}">
                학수번호
              </th>
              <th class="table-header" @click="sortTableForAll('commit')" :style="{width: tablewidth(headerforall[7][1])}">
                Commit
              </th>
              <th class="table-header" @click="sortTableForAll('pr')" :style="{width: tablewidth(headerforall[8][1])}">
                PR
              </th>
              <th class="table-header" @click="sortTableForAll('issue')" :style="{width: tablewidth(headerforall[9][1])}">
                Issue
              </th>
              <th class="table-header" @click="sortTableForAll('num_repos')" :style="{width: tablewidth(headerforall[10][1])}">
                Repos
              </th>
>>>>>>> origin/dev-jhs
            </thead>
            <tbody>
              <tr v-for="(item, index) in sclicedPosts" :key="index" class="table-row">
                <td :title="item.yearandsemester">{{item.yearandsemester}}</td>
                <td :title="item.name">{{item.name}}</td>
                <td :title="item.department">{{item.department}}</td>
                <td :title="item.id">{{item.id}}</td>
                <td :title="item.enrollment">{{item.enrollment}}</td>
                <td :title="item.github">{{item.github}}</td>
                <td :title="item.course_name">{{item.course_name}}</td>
                <td :title="item.course_id">{{item.course_id}}</td>
                <td :title="item.commit">{{item.commit}}</td>
                <td :title="item.pr">{{item.pr}}</td>
                <td :title="item.issue">{{item.issue}}</td>
                <td :title="item.num_repos">{{item.num_repos}}</td>
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
      </transition>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InformationStudent',
  props: ["postss"],
  data() {
    return {
<<<<<<< HEAD
=======
      currentSort: null, // 현재 정렬 중인 열
      currentSortDir: 'asc', // 정렬 방향 (asc: 오름차순, desc: 내림차순)
>>>>>>> origin/dev-jhs
      showTable: false,
      searchField: '',
      pannelLoading: false,
      posts: [],
      sclicedPosts: [],
      summarizedStudents : [],
      slicedsummarizedStudents : [],
      currentPageforAll: 1,
      currentPageforSummary: 1,
      postsPerPage: 10,
      headerforall: [['개설학기', '5%'], 
               ['이름', '10%'], 
               ['학과', '12%'], 
               ['학번', '8%'], 
               ['학적', '5%'],
               ['Github ID', '11%'], 
               ['과목명', '13%'], 
               ['학수번호', '8%'], 
               ['Commit', '7%'], 
               ['PR', '7%'], 
               ['Issue', '7%'], 
               ['Repos', '7%']],
      headerforsummary: [
               ['이름', '10%'], 
               ['학과', '17%'], 
               ['학번', '12%'], 
               ['학적', '8%'],
               ['Github ID', '13%'], 
               ['Commit', '10%'], 
               ['PR', '10%'], 
               ['Issue', '10%'], 
               ['Repos', '10%']],
    };
  },
  computed: {
    totalPagesforAll() {
      return Math.ceil(this.postss.length / this.postsPerPage);
    },
    totalPagesforSummary() {
      return Math.ceil(this.summarizedStudents.length / this.postsPerPage);
    },
    totalPagesPerListforAll() {
      return  Math.floor(Math.ceil(this.postss.length / this.postsPerPage) / 10) + 1;
    },
    totalPagesPerListforSummary() {
      return  Math.floor(Math.ceil(this.summarizedStudents.length / this.postsPerPage) / 10) + 1;
    },
    prevPageDisabledforAll() {
      return Math.floor((this.currentPageforAll - 1) / 10) === 0
    },
    prevPageDisabledforSummary() {
      return Math.floor((this.currentPageforSummary - 1) / 10) === 0
    },
    nextPageDisabledforAll() {
      return Math.floor((this.currentPageforAll - 1) / 10) + 1 >= this.totalPagesPerListforAll
    },
    nextPageDisabledforSummary() {
      return Math.floor((this.currentPageforSummary - 1) / 10) + 1 >= this.totalPagesPerListforSummary
    },
    firstPageDisabledforAll() {
      return this.currentPageforAll === 1
    },
    firstPageDisabledforSummary() {
      return this.currentPageforSummary === 1
    },
    lastPageDisabledforAll() {
      return this.currentPageforAll === this.totalPagesforAll
    },
    lastPageDisabledforSummary() {
      return this.currentPageforSummary === this.totalPagesforSummary
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
    pagesToShowforSummary() {
      const startPage = Math.floor((this.currentPageforSummary - 1) / 10) * 10 + 1;
      const endPage = Math.min(startPage + 9, this.totalPagesforSummary);
      const pages = [];
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
      return pages;
    }
  },
  methods: {
<<<<<<< HEAD
=======
    // 정렬 메서드
    sortTable(column) {
      if (this.currentSort === column) {
        // 같은 열을 다시 클릭하면 정렬 방향 변경
        this.currentSortDir = this.currentSortDir === 'asc' ? 'desc' : 'asc';
      } else {
        // 새로운 열 클릭 시 오름차순으로 정렬 시작
        this.currentSort = column;
        this.currentSortDir = 'asc';
      }

      // 전체 데이터인 summarizedStudents 배열을 정렬
      this.summarizedStudents.sort((a, b) => {
        let modifier = this.currentSortDir === 'asc' ? 1 : -1;
        if (a[column] < b[column]) return -1 * modifier;
        if (a[column] > b[column]) return 1 * modifier;
        return 0;
      });

      // 정렬된 데이터를 페이지에 맞게 나눠서 보여주기
      this.slicingforsummary();
    },
    sortTableForAll(column) {
      if (this.currentSort === column) {
        // 같은 열을 다시 클릭하면 정렬 방향을 변경
        this.currentSortDir = this.currentSortDir === 'asc' ? 'desc' : 'asc';
      } else {
        // 새로운 열을 클릭하면 오름차순으로 정렬 시작
        this.currentSort = column;
        this.currentSortDir = 'asc';
      }

      // 전체 데이터인 posts 배열을 정렬
      this.posts.sort((a, b) => {
        let modifier = this.currentSortDir === 'asc' ? 1 : -1;
        if (a[column] < b[column]) return -1 * modifier;
        if (a[column] > b[column]) return 1 * modifier;
        return 0;
      });

      // 정렬된 데이터를 페이지에 맞게 나눠서 보여줌
      this.slicingforall();
    },
>>>>>>> origin/dev-jhs
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
    changePageforSummary(page) {
      let toPage = 0
      if (page < 1) {
        toPage = 1;  
      } else if (page > this.totalPagesforSummary) {
        toPage = this.totalPagesforSummary;
      } else {
        toPage = page;
      }
      const query = { ...this.$route.query, page: toPage };
      this.$router.replace({ path: this.$route.path, query: query });
      this.currentPageforSummary = toPage;
    },
    firstPageforAll() {
      if (this.currentPageforAll > 1) {
        this.changePageforAll(1);
      }
    },
    firstPageforSummary() {
      if (this.currentPageforSummary > 1) {
        this.changePageforSummary(1);
      }
    },
    prevPageforAll() {
      if (this.currentPageforAll > 1) {
        this.changePageforAll(Math.floor((this.currentPageforAll - 1) / 10));
      }
    },
    prevPageforSummary() {
      if (this.currentPageforSummary > 1) {
        this.changePageforSummary(Math.floor((this.currentPageforSummary - 1) / 10));
      }
    },
    nextPageforAll() {
      if (Math.floor((this.currentPageforAll - 1) / 10) + 1 < this.totalPagesPerListforAll) {
        this.changePageforAll(Math.floor((this.currentPageforAll - 1) / 10) + 11);
      }
    },
    nextPageforSummary() {
      if (Math.floor((this.currentPageforSummary - 1) / 10) + 1 < this.totalPagesPerListforSummary) {
        this.changePageforSummary(Math.floor((this.currentPageforSummary - 1) / 10) + 11);
      }
    },
    lastPageforAll() {
      if (this.currentPageforAll < this.totalPagesforAll) {
        this.changePageforAll(this.totalPagesforAll);
      }
    },
    lastPageforSummary() {
      if (this.currentPageforSummary < this.totalPagesforSummary) {
        this.changePageforSummary(this.totalPagesforSummary);
      }
    },
    toggle() {
      this.showTable = !this.showTable;
    },
    tablewidth(length) {
      return length;
    },
    slicingforall() {
      const start = (this.currentPageforAll - 1) * this.postsPerPage;
      const end = start + this.postsPerPage;
<<<<<<< HEAD
      this.sclicedPosts = this.yearandCommitSort(this.posts.slice(start, end));
=======
      // 정렬된 posts 배열에서 현재 페이지에 해당하는 부분만 가져옴
      this.sclicedPosts = this.posts.slice(start, end);
>>>>>>> origin/dev-jhs
    },
    slicingforsummary() {
      const start = (this.currentPageforSummary - 1) * this.postsPerPage;
      const end = start + this.postsPerPage;
<<<<<<< HEAD
      this.slicedsummarizedStudents = this.commitSort(this.summarizedStudents.slice(start, end));
=======
      // 정렬된 summarizedStudents에서 현재 페이지에 해당하는 부분만 가져옴
      this.slicedsummarizedStudents = this.summarizedStudents.slice(start, end);
>>>>>>> origin/dev-jhs
    },
    commitSort(li){
      li.sort(function(a,b){
        if( !a.commit ) {
          a.commit = 0
        }
        if(!b.commit) {
          b.commit = 0
        }
        return b.commit - a.commit
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
          newData.enrollment = element.enrollment
          newData.department = element.department
          newData.github = element.github
          newData.commit = element.commit
          newData.pr = element.pr
          newData.issue = element.issue
          newData.num_repos = element.num_repos
          ret[index] = newData
        }
        else {
          var appendData = ret[index]
          appendData.commit = appendData.commit + element.commit
          appendData.pr = appendData.pr + element.pr
          appendData.issue = appendData.issue + element.issue
          appendData.num_repos = appendData.num_repos + element.num_repos
          ret[index] = appendData   
        }
      });
      ret = this.commitSort(ret)
      this.summarizedStudents = ret
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
    this.posts = this.postss;
    this.currentPageforAll = parseInt(this.$route.query.page) || 1;
    this.slicingforall();
    this.toSummarized(this.posts);
    this.slicingforsummary();
  },
  beforeMount() {
    const query = this.$route.query;
    const newQuery = { ...query };
    let needsReplace = false;
    if (!query.page) {
      newQuery.page = 1;
      needsReplace = true;
    }
    if (!query.type) {
      newQuery.type = 'summary';
      needsReplace = true;
    }
    if (query.type && query.type !== 'summary' && query.type !== 'all') {
      newQuery.type = 'summary';
      needsReplace = true;
    }
    if (needsReplace) {
      this.$router.replace({ path: this.$route.path, query: newQuery });
    }

    if (newQuery.type === 'summary') {
      this.showTable = false;
    } else if (newQuery.type === 'all') {
      this.showTable = true;
    }
    this.currentPageforAll = parseInt(query.page) || 1;
  },
  watch: {
    postss(to, from) {
      this.posts = to;
      this.slicingforall();
      if (this.$route.query.type === 'all' && this.$route.query.page > this.totalPagesforAll) {
        this.changePageforAll(this.totalPagesforAll);
      }
      this.toSummarized(this.posts);
      this.slicingforsummary();
      if (this.$route.query.type === 'summary' && this.$route.query.page > this.totalPagesforSummary) {
        this.changePageforSummary(this.totalPagesforSummary);
      }
    },
    $route(to, from) {
      this.currentPageforAll = parseInt(to.query.page) || 1;
      console.log('to is ', to)
      console.log('from is ', from)
      // type이 변경된 경우 currentPage를 1로 설정
      if (to.query.type !== from.query.type) {
        this.currentPageforAll = 1;
      }
      this.slicingforall();
      this.toSummarized(this.posts);
      this.slicingforsummary();
    },
    currentPageforAll(to, from) {
      this.slicingforall();
      this.toSummarized(this.posts);
      this.slicingforsummary();
    },
  }
};
</script>

<style scoped>
.container {
  max-width: 1600px;
  .navigation {
    min-height: 41px;
    padding-left: 56px;
    padding-right: 56px;
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
      transition: border-bottom 0.2s ease-in-out;
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
    .form-field:focus::before, .form-field:focus::after {
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
  .toggle-box {
    .wrapper {
      width: 150px;
      height: 44px;
      text-align: center;
      margin: 0 auto;
      position: relative;
    }
    #infoswitchstudent {
      display: none;
    }
    .switch_label {
      position: relative;
      cursor: pointer;
      display: inline-block;
      width: 150px;
      height: 41px;
      background: #ffe2e5;
      border-radius: 20px;
      transition: 0.4s;
    }
    .onf_btn {
      position: absolute;
      top: 4px;
      left: 3px;
      width: 75px;
      height: 33px;
      border-radius: 20px;
      background: white;
      transition: 0.2s;
      box-shadow: 1px 2px 3px #00000020;
    }
    .toggle-text {
      position: absolute;
      line-height: 41px;
      height: 41px;
      width: 150px;
      display: flex;
      justify-content: flex-start;
      vertical-align: middle;
      padding: 6px 26px;
      .toggle-total,
      .toggle-indiv {
        color: var(--Primary_medium, #CB385C);
        height: 29px;
        line-height: 29px;
        font-family: Pretendard;
        font-size: 16px;
        font-weight: 600;
      }
      .toggle-total {
        color: var(--Primary_medium, #CB385C);
        margin-right: auto;
        transition: color 0.2s linear;
      }
      .toggle-indiv {
        color: var(--Primary_disabled, #E9D8D9);
        transition: color 0.2s linear;
      }
    }
    #infoswitchstudent:checked + .switch_label .onf_btn {
      left: 70px;
      background: #fff;
      box-shadow: 1px 2px 3px #00000020;
    }
    #infoswitchstudent:checked + .switch_label .toggle-total {
      color: var(--Primary_disabled, #E9D8D9);
      & path {
        stroke: #E9D8D9;
      }
    }
    #infoswitchstudent:checked + .switch_label .toggle-indiv {
      color: var(--Primary_medium, #CB385C);
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
  .table-header-wrapper {
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
</style>
