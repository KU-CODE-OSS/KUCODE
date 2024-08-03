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
          <input type="checkbox" id="switch" v-model="showTable">
          <label for="switch" class="switch_label">
            <span class="onf_btn"></span>
            <div class="toggle-text">
                <div class="toggle-total">
                  전체
                </div>
                <div class="toggle-indiv">
                    개별
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
        </div>
        <div v-else class="table">
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
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import {getCourseInfo, postCourseUpload} from '@/api.js'

export default {
  name: 'InformationStudent',
  props: ["postss"],
  data() {
    return {
      showTable: false,
      searchField: '',
      pannelLoading: false,
      posts: [],
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
    };
  },
  computed: {
    totalPages() {
      return Math.ceil(this.posts.length / this.postsPerPage)
    },
  },
  methods: {
    selectFile(e) {
      this.selectedFile = e.target.files[0];
      this.selectedFileName = this.selectedFile.name
      console.log(this.selectedFile)
    },
    toggle() {
      this.showTable = !this.showTable;
    },
    tablewidth(length) {
      return length
    },
  },
  mounted() {
    this.posts = this.postss
  },
  watch: {
    postss(to, from) {
      const vm = this
      this.posts = vm.postss
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

  .toggle-box {
    .wrapper {
      width: 150px;
      height: 44px;
      text-align: center;
      margin: 0 auto;
      position: relative;
    }

    #switch {
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
        .toggle-total, .toggle-indiv {
          color: var(--Primary_medium, #CB385C);
          height: 29px;
          line-height: 29px;
          /* color: var(--Primary_disabled, #E9D8D9); */
          /* text-sm */
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
    #switch:checked + .switch_label .onf_btn {
        left: 70px;
        background: #fff;
        box-shadow: 1px 2px 3px #00000020;
    }
    #switch:checked + .switch_label .toggle-total {
      color: var(--Primary_disabled, #E9D8D9);
        & path {
            stroke: #E9D8D9;
        }
    }
    #switch:checked + .switch_label .toggle-indiv {
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
  }
}

.table,
.chart {
  margin: 20px 0;
  padding: 20px 0;
  border: 1px solid #dce2ed;
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
