<!-- 학생 데이터 -->
<template>
    <v-data-table :headers="headers" :items="items"></v-data-table>

  <div></div>
</template>

<script>
export default {
  name: 'App',
  components: {
  },
  data() {
      return {
        dialog: false,
        headers: [
          { text: 'StudentID', value: 'StudentID' },
          { text: 'StudentNM', value: 'StudentNM' },
          { text: 'Department', value: 'Department' },
          { text: 'DoubleMajor', value: 'DoubleMajor' },
          { text: 'StudentNumber', value: 'StudentNumber' },
          { text: 'College', value: 'College' },
          { text: 'Primary_Email', value: 'Primary_Email' },
          { text: 'EnrollmentStatus', value: 'EnrollmentStatus' },
          { text: 'Follower_cnt', value: 'Follower_cnt' },
          { text: 'Following_cnt', value: 'Following_cnt' },
          { text: 'Public_repos_cnt', value: 'Public_repos_cnt' },
          { text: 'Github_profile_createDate', value: 'Github_profile_createDate' },
          { text: 'Github_profile_updateDate', value: 'Github_profile_updateDate' },          
          // 나머지 헤더 필드도 동일하게 추가
          { text: 'Actions', value: 'actions', sortable: false },
        ],
        items: [
          {
            StudentID: 123123101,
            StudentNM: '홍길동',
            Department: '컴퓨터공학과', 
            DoubleMajor: '경영학과', 
            StudentNumber: '20240001', 
            College: '공과대학', 
            Primary_Email: 'hong101@university.ac.kr', 
            EnrollmentStatus: '재학', 
            Follower_cnt: 120, 
            Following_cnt: 75, 
            Public_repos_cnt: 30, 
            Github_profile_createDate: '2019-02-15', 
            Github_profile_updateDate: '2024-03-22'
            // 나머지 필드도 동일하게 추가
          },
          {
            StudentID: 102, 
            StudentNM: '이순신', 
            Department: '기계공학과', 
            DoubleMajor: '없음', 
            StudentNumber: '20240002', 
            College: '공과대학', 
            Primary_Email: 'lee102@university.ac.kr', 
            EnrollmentStatus: '휴학', 
            Follower_cnt: 150, 
            Following_cnt: 80, 
            Public_repos_cnt: 12, 
            Github_profile_createDate: '2018-06-10', 
            Github_profile_updateDate: '2024-01-18'
          },
          {
            StudentID: 103, 
            StudentNM: '장보고', 
            Department: '전자공학과', 
            DoubleMajor: '물리학과', 
            StudentNumber: '20240003', 
            College: '자연과학대학', 
            Primary_Email: 'jang103@university.ac.kr', 
            EnrollmentStatus: '졸업', 
            Follower_cnt: 200, 
            Following_cnt: 100, 
            Public_repos_cnt: 42, 
            Github_profile_createDate: '2017-11-30', 
            Github_profile_updateDate: '2024-03-20'
          },
        ],
        editedIndex: -1,
        editedItem: {
        StudentID: null,
        StudentNM: '',
        Department: '',
        DoubleMajor: '',
        StudentNumber: '',
        College: '',
        Primary_Email: '',
        EnrollmentStatus: '',
        Follower_cnt: null,
        Following_cnt: null,
        Public_repos_cnt: null,
        Github_profile_createDate: '',
        Github_profile_updateDate: '',
        },
        defaultItem: {
        StudentID: null,
        StudentNM: '',
        Department: '',
        DoubleMajor: '',
        StudentNumber: '',
        College: '',
        Primary_Email: '',
        EnrollmentStatus: '',
        Follower_cnt: null,
        Following_cnt: null,
        Public_repos_cnt: null,
        Github_profile_createDate: '',
        Github_profile_updateDate: '',
        },
      }
    },
}
  
</script>