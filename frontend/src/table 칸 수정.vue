<template>
    <v-text-field
      v-model="search"
      label="Search"
      prepend-inner-icon="mdi-magnify"
      variant="outlined"
      hide-details
      single-line
    ></v-text-field>
    <v-data-table
      :group-by="groupBy"
      :headers="headers"
      :items="filteredStudents"
      item-value="name"
    >
      <template v-slot:group-header="{ item, columns, toggleGroup, isGroupOpen }">
        <tr>
          <td>
            <v-btn
              :icon="isGroupOpen(item) ? '$expand' : '$next'"
              size="small"
              variant="text"
              @click="toggleGroup(item)"
            ></v-btn>
          </td>
          <td>{{ groupInfo[item.value]?.name }}</td>
  
          <td>{{ groupInfo[item.value]?.department }}</td>
          <td>{{ groupInfo[item.value]?.id }}</td>
          <td>{{ groupInfo[item.value]?.enrollment }}</td>
          <td>{{ groupInfo[item.value]?.github_id }}</td>
          <td>{{ groupInfo[item.value]?.year }}</td>
          <td>{{ groupInfo[item.value]?.semester }}</td>
          <td>{{ groupInfo[item.value]?.course_name }}</td>
          <td>{{ groupInfo[item.value]?.commit }}</td>
          <td>{{ groupInfo[item.value]?.pr }}</td>
          <td>{{ groupInfo[item.value]?.issue }}</td>
          <td>{{ groupInfo[item.value]?.num_repos }}</td>
        </tr>
      </template>
      <template v-slot:item="{ item }">
        <tr>
          <td></td>
          <td></td>
          <!-- 빈 필드를 추가하여 group-header와 일치시킴 -->
  
          <td>{{ item.department }}</td>
          <td>{{ item.id }}</td>
          <td>{{ item.enrollment }}</td>
          <td>{{ item.github_id }}</td>
          <td>{{ item.year }}</td>
          <td>{{ item.semester }}</td>
          <td>{{ item.course_name }}</td>
          <td>{{ item.commit }}</td>
          <td>{{ item.pr }}</td>
          <td>{{ item.issue }}</td>
          <td>{{ item.num_repos }}</td>
        </tr>
      </template>
    </v-data-table>
  </template>
  
  <script>
    export default {
      data() {
        return {
          search: '',
          groupBy: [
            {
              key: 'name',
              order: 'asc',
            },
          ],
          headers: [
            { title: 'Name', key: 'name' },
  
            { title: 'Department', key: 'department' },
            { title: 'ID', key: 'id' },
            { title: 'Enrollment', key: 'enrollment' },
            { title: 'Github_id', key: 'github_id' },
            { title: 'Year', key: 'year' },
            { title: 'Semester', key: 'semester' },
            { title: 'Course_name', key: 'course_name' },
            { title: 'Commit', key: 'commit' },
            { title: 'PR', key: 'pr' },
            { title: 'Issue', key: 'issue' },
            { title: 'Num_repos', key: 'num_repos' },
          ],
          students: [
            {
              name: '정창환',
              year: 2024,
              semester: 1,
              department: '',
              id: '',
              enrollment: '',
              github_id: '',
              course_name: '운영체제',
              commit: 8,
              pr: 0,
              issue: 0,
              num_repos: 1,
            },
            {
              name: '정창환',
              year: 2024,
              semester: 1,
              department: '',
              id: '',
              enrollment: '',
              github_id: '',
              course_name: '데이터베이스',
              commit: 3,
              pr: 1,
              issue: 0,
              num_repos: 1,
            },
            {
              name: '정현승',
              year: 2024,
              semester: 1,
              department: '',
              id: '',
              enrollment: '',
              github_id: '',
              course_name: '운영체제',
              commit: 14,
              pr: 2,
              issue: 5,
              num_repos: 12,
            },
            {
              name: '정현승',
              year: 2024,
              semester: 1,
              department: '',
              id: '',
              enrollment: '',
              github_id: '',
              course_name: '네트워크',
              commit: 7,
              pr: 1,
              issue: 1,
              num_repos: 3,
            },
            {
              name: '김명준',
              year: 2024,
              semester: 1,
              department: '',
              id: '',
              enrollment: '',
              github_id: '',
              course_name: '운영체제',
              commit: 143,
              pr: 21,
              issue: 52,
              num_repos: 43,
            },
            {
              name: '김명준',
              year: 2024,
              semester: 1,
              department: '',
              id: '',
              enrollment: '',
              github_id: '',
              course_name: '알고리즘',
              commit: 10,
              pr: 2,
              issue: 1,
              num_repos: 5,
            },
          ],
          groupInfo: {
            정창환: {
              year: '',
              semester: '',
              name: '정창환',
              department: '컴퓨터학과',
              id: '2019021104',
              enrollment: '재학',
              github_id: 'jch1203',
              course_name: '',
              commit: 11,
              pr: 1,
              issue: '0', // 0을 숫자로 넣으면 출력 안 됨
              num_repos: 2,
            },
            정현승: {
              year: '',
              semester: '',
              name: '정현승',
              department: '컴퓨터학과',
              id: '2019021432',
              enrollment: '재학',
              github_id: 'okhs0712',
              course_name: '',
              commit: 21,
              pr: 3,
              issue: 6,
              num_repos: 15,
            },
            김명준: {
              year: '',
              semester: '',
              name: '김명준',
              department: '컴퓨터학과',
              id: '2023021649',
              enrollment: '재학',
              github_id: 'johnkim',
              course_name: '',
              commit: 153,
              pr: 23,
              issue: 53,
              num_repos: 48,
            },
          },
        }
      },
      computed: {
        filteredStudents() {
          const search = this.search.toLowerCase()
          return this.students.filter(student => {
            const group = this.groupInfo[student.name]
            return (
              student.name.toLowerCase().includes(search) ||
              (group.year && group.year.toString().includes(search)) ||
              (group.semester && group.semester.toString().includes(search)) ||
              group.name.toLowerCase().includes(search) ||
              group.department.toLowerCase().includes(search) ||
              group.id.toLowerCase().includes(search) ||
              group.enrollment.toLowerCase().includes(search) ||
              group.github_id.toLowerCase().includes(search) ||
              (group.course_name &&
                group.course_name.toLowerCase().includes(search)) ||
              group.commit.toString().includes(search) ||
              group.pr.toString().includes(search) ||
              group.issue.toString().includes(search) ||
              group.num_repos.toString().includes(search)
            )
          })
        },
      },
    }
  </script>
  