<template>
  <div>
    <v-toolbar flat color="white">
      <v-toolbar-title>Students</v-toolbar-title>
      <v-divider class="mx-2" inset vertical></v-divider>
      <v-spacer></v-spacer>
      <v-btn color="primary" dark class="mb-2" @click="dialog = true"
        >New Item</v-btn
      >
    </v-toolbar>
    <v-dialog v-model="dialog" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">{{ formTitle }}</span>
        </v-card-title>
        <v-card-text>
          <v-container grid-list-md>
            <v-row wrap>
              <v-col xs="12" sm="12" md="6">
                <v-text-field
                  v-model="editedItem.StudentID"
                  label="Student ID"
                ></v-text-field>
              </v-col>
              <v-col xs="12" sm="12" md="6">
                <v-text-field
                  v-model="editedItem.StudentNM"
                  label="Student Name"
                ></v-text-field>
              </v-col>

              <v-col xs="12" sm="12" md="6">
                <v-text-field
                  v-model="editedItem.Department"
                  label="Department"
                ></v-text-field>
              </v-col>

              <v-col xs="12" sm="12" md="6">
                <v-text-field
                  v-model="editedItem.DoubleMajor"
                  label="DoubleMajor"
                ></v-text-field>
              </v-col>

              <v-col xs="12" sm="12" md="6">
                <v-text-field
                  v-model="editedItem.StudentNumber"
                  label="StudentNumber"
                ></v-text-field>
              </v-col>

              <v-col xs="12" sm="12" md="6">
                <v-text-field
                  v-model="editedItem.College"
                  label="College"
                ></v-text-field>
              </v-col>

              <v-col xs="12" sm="12" md="6">
                <v-text-field
                  v-model="editedItem.Primary_Email"
                  label="Primary_Email"
                ></v-text-field>
              </v-col>

              <v-col xs="12" sm="12" md="6">
                <v-text-field
                  v-model="editedItem.EnrollmentStatus"
                  label="EnrollmentStatus"
                ></v-text-field>
              </v-col>

              <v-col xs="12" sm="12" md="6">
                <v-text-field
                  v-model="editedItem.Follower_cnt"
                  label="Follower_cnt"
                ></v-text-field>
              </v-col>

              <v-col xs="12" sm="12" md="6">
                <v-text-field
                  v-model="editedItem.Following_cnt"
                  label="Following_cnt"
                ></v-text-field>
              </v-col>

              <v-col xs="12" sm="12" md="6">
                <v-text-field
                  v-model="editedItem.Public_repos_cnt"
                  label="Public_repos_cnt"
                ></v-text-field>
              </v-col>

              <v-col xs="12" sm="12" md="6">
                <v-text-field
                  v-model="editedItem.Github_profile_createDate"
                  label="Github_profile_createDate"
                ></v-text-field>
              </v-col>

              <v-col xs="12" sm="12" md="6">
                <v-text-field
                  v-model="editedItem.Github_profile_updateDate"
                  label="Github_profile_updateDate"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" flat @click="close">Cancel</v-btn>
          <v-btn color="blue darken-1" flat @click="save">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-data-table :headers="headers" :items="items" class="elevation-1">
      <template v-slot:items="props">
        <td>{{ props.item.StudentID }}</td>
        <td>{{ props.item.StudentNM }}</td>
        <td>{{ props.item.Department }}</td>
        <td>{{ props.item.DoubleMajor }}</td>
        <td>{{ props.item.StudentNumber }}</td>
        <td>{{ props.item.College }}</td>
        <td>{{ props.item.Primary_Email }}</td>
        <td>{{ props.item.EnrollmentStatus }}</td>
        <td>{{ props.item.Follower_cnt }}</td>
        <td>{{ props.item.Following_cnt }}</td>
        <td>{{ props.item.Public_repos_cnt }}</td>
        <td>{{ props.item.Github_profile_createDate }}</td>
        <td>{{ props.item.Github_profile_updateDate }}</td>

        <!-- 나머지 필드도 동일하게 추가 -->
        <td class="justify-center layout px-0">
          <v-icon small class="mr-2" @click="editItem(props.item)">edit</v-icon>
          <v-icon small @click="deleteItem(props.item)">delete</v-icon>
        </td>
      </template>
      <template v-slot:no-data>
        <v-btn color="primary" @click="reset">Reset</v-btn>
      </template>
    </v-data-table>
  </div>
</template>

<script>
  export default {
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
          {
            text: 'Github_profile_createDate',
            value: 'Github_profile_createDate',
          },
          {
            text: 'Github_profile_updateDate',
            value: 'Github_profile_updateDate',
          },
          // 나머지 헤더 필드도 동일하게 추가
          { text: 'Actions', value: 'actions', sortable: false },
        ],
        items: [
          {
            StudentID: 101,
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
            Github_profile_updateDate: '2024-03-22',
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
            Github_profile_updateDate: '2024-01-18',
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
            Github_profile_updateDate: '2024-03-20',
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
    computed: {
      formTitle() {
        return this.editedIndex === -1 ? 'New Item' : 'Edit Item'
      },
    },

    methods: {
      editItem(item) {
        this.editedIndex = this.items.indexOf(item)
        this.editedItem = Object.assign({}, item)
        this.dialog = true
      },

      deleteItem(item) {
        const index = this.items.indexOf(item)
        if (confirm('Are you sure you want to delete this item?')) {
          this.items.splice(index, 1)
        }
      },

      close() {
        this.dialog = false
        setTimeout(() => {
          this.editedItem = Object.assign({}, this.defaultItem)
          this.editedIndex = -1
        }, 300)
      },

      save() {
        if (this.editedIndex > -1) {
          Object.assign(this.items[this.editedIndex], this.editedItem)
        } else {
          this.items.push(this.editedItem)
        }
        this.close()
      },

      reset() {
        this.items = []
        this.initialize()
      },

      initialize() {
        // 초기 데이터를 추가하는 부분입니다.
        // 필요에 따라서 데이터를 초기화할 수 있습니다.
      },
    },
  }
</script>
