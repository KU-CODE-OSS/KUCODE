<template>
  <portal to="stat_table_major">
    <filters
      class="filter-container"
      :students="items"
      @update:filteredStudents="updateFilteredItems"
    ></filters>
  </portal>
  <div>
    <!-- <v-toolbar flat color="white">
      <v-divider class="mx-2" inset vertical></v-divider>
      <v-spacer></v-spacer>
      <v-col cols="2" align="right">
        <v-text-field
          v-model="search"
          label="Search"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          hide-details
          single-line          
        ></v-text-field>
      </v-col>
      <v-btn color="primary" dark class="mb-2" @click="importDialog = true" prepend-icon="mdi-import">Import</v-btn>
      <v-btn color="primary" dark class="mb-2" @click="dialog = true" prepend-icon="mdi-plus">New Item</v-btn>
    </v-toolbar> -->
    <v-dialog v-model="importDialog" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">Import Course</span>
        </v-card-title>
        <v-card-text>
          <v-container grid-list-md>
            <v-row wrap>
              <v-col xs="12" sm="12" md="6">
                <v-text-field v-model="importItem.course_id" label="학수번호"></v-text-field>
              </v-col>
              <v-col xs="12" sm="12" md="6">
                <v-text-field v-model="importItem.year" label="연도"></v-text-field>
              </v-col>
              <v-col xs="12" sm="12" md="6">
                <v-text-field v-model="importItem.semester" label="학기"></v-text-field>
              </v-col>
              <v-col xs="12" sm="12" md="6">
                <v-text-field v-model="importItem.name" label="과목명"></v-text-field>
              </v-col>
              <v-col xs="12" sm="12" md="6">
                <v-text-field v-model="importItem.prof" label="교수"></v-text-field>
              </v-col>
              <v-col xs="12" sm="12" md="6">
                <v-text-field v-model="importItem.ta" label="조교"></v-text-field>
              </v-col>
              <v-col xs="12" sm="12" md="6">
                <v-text-field v-model="importItem.student_count" label="Student Count"></v-text-field>
              </v-col>
              <v-col xs="12" sm="12" md="12">
                <v-text-field v-model="importItem.course_repo_name" label="Course Repo Name"></v-text-field>
              </v-col>
              <v-col xs="12" sm="12" md="12">
                <input type="file" @change="selectFile" accept=".xlsx, .xls, .csv" />
              </v-col>
            </v-row>  
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" flat @click="closeImportDialog">Cancel</v-btn>
          <v-btn color="blue darken-1" flat @click="handleFileUpload">Import</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-data-table
      :headers="courseHeaders"
      :items="filteredItemsBySearch"
      class="elevation-1"
      :loading="loading"
    >
      <template v-slot:item="{ item }">
        <tr>
          <td>{{ item.year }}</td>
          <td>{{ item.semester }}</td>
          <td>{{ item.name }}</td>
          <td>{{ item.course_id }}</td>
          <td>{{ item.prof }}</td>
          <td>{{ item.ta }}</td>
          <td>{{ item.student_count }}</td>
          <td>{{ item.total_commits }}</td>
          <td>{{ item.avg_commits }}</td>
          <td>{{ item.repository_count }}</td>
          <td>{{ item.contributor_count }}</td>
        </tr>
      </template>
      <template v-slot:no-data>
        <v-btn color="primary" @click="reset">Reset</v-btn>
      </template>
    </v-data-table>
  </div>
</template>

<script>
import axios from 'axios';
import * as XLSX from 'xlsx';
import Filters from './table_major_filters.vue';

export default {
  components: {
    Filters,
  },
  data() {
    return {
      loading: true,
      search: '',
      dialog: false,
      importDialog: false,
      selectedFile: null,
      courseHeaders: [
        { align: 'center', title: '연도', key: 'year' },
        { align: 'center', title: '학기', key: 'semester' },
        { align: 'center', title: '과목명', key: 'name' },
        { align: 'center', title: '학수번호', key: 'course_id' },
        { align: 'center', title: '교수', key: 'prof' },
        { align: 'center', title: '조교', key: 'ta' },
        { align: 'center', title: '학생 수', key: 'student_count' },
        { align: 'center', title: '총 Commit 수', key: 'total_commits' },
        { align: 'center', title: '평균 Commit 수', key: 'avg_commits' },
        { align: 'center', title: 'Repo 수', key: 'repository_count' },
        { align: 'center', title: '기여자 수', key: 'contributor_count' },
      ],
      items: [],
      students: [],
      filteredItems: [],
      editedIndex: -1,
      editedItem: {
        year: null,
        semester: '',
        name: '',
        course_id: '',
        prof: '',
        ta: '',
        student_count: '',
        total_commits: '',
        avg_commits: null,
        repository_count: null,
        contributor_count: null,
      },
      importItem: {
        course_id: '',
        year: '',
        semester: '',
        name: '',
        prof: '',
        ta: '',
        student_count: '',
        course_repo_name: '',
      },
      defaultItem: {
        year: null,
        semester: '',
        name: '',
        course_id: '',
        prof: '',
        ta: '',
        student_count: '',
        total_commits: '',
        avg_commits: null,
        repository_count: null,
        contributor_count: null,
      },
    }
  },
  computed: {
    formTitle() {
      return this.editedIndex === -1 ? 'New Item' : 'Edit Item';
    },
    filteredItemsBySearch() {
      const search = this.search.toLowerCase();
      return this.filteredItems.filter(item => {
        const semester = item.semester ? item.semester.toString().toLowerCase() : '';
        const name = item.name ? item.name.toLowerCase() : '';
        const courseId = item.course_id ? item.course_id.toLowerCase() : '';
        const prof = item.prof ? item.prof.toLowerCase() : '';
        const ta = item.ta ? item.ta.toLowerCase() : '';
        const studentCount = item.student_count ? item.student_count.toString() : '';
        const totalCommits = item.total_commits ? item.total_commits.toString() : '';
        const avgCommits = item.avg_commits ? item.avg_commits.toString() : '';
        const repoCount = item.repository_count ? item.repository_count.toString() : '';
        const contributorCount = item.contributor_count ? item.contributor_count.toString() : '';

        return (
          item.year.toString().includes(search) ||
          semester.includes(search) ||
          name.includes(search) ||
          courseId.includes(search) ||
          prof.includes(search) ||
          ta.includes(search) ||
          studentCount.includes(search) ||
          totalCommits.includes(search) ||
          avgCommits.includes(search) ||
          repoCount.includes(search) ||
          contributorCount.includes(search)
        );
      });
    },
  },
  methods: {
    selectFile(event) {
      this.selectedFile = event.target.files[0];
    },
    async handleFileUpload() {
      if (!this.selectedFile) {
        alert('Please select a file.');
        return;
      }

      const reader = new FileReader();
      reader.onload = async (e) => {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });

        const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
        const sheetData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });

        // Insert the import item details as the first row
        const importDetails = [
          this.importItem.course_id,
          this.importItem.year,
          this.importItem.semester,
          this.importItem.name,
          this.importItem.prof,
          this.importItem.ta,
          this.importItem.student_count,
          this.importItem.course_repo_name,
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
        formData.append('name', this.importItem.name);
        formData.append('prof', this.importItem.prof);
        formData.append('ta', this.importItem.ta);
        formData.append('student_count', this.importItem.student_count);
        formData.append('course_repo_name', this.importItem.course_repo_name);
      
      try {
        const response = await axios.post('http://localhost/api/account/student_excel_import', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        console.log('File imported successfully:', response);
          this.closeImportDialog();
      } catch (error) {
        console.error('Error importing file:', error);
      }
      };
      reader.readAsArrayBuffer(this.selectedFile);
    },
    closeImportDialog() {
      this.importDialog = false;
      this.importItem = {
        course_id: '',
        year: '',
        semester: '',
        name: '',
        prof: '',
        ta: '',
        student_count: '',
        course_repo_name: '',
      };
      this.selectedFile = null;
    },
    async fetchData() {
      try {
        this.loading = true;
        const response = await axios.get('http://localhost/api/course/course_read_db');
        console.log('API Response:', response.data); // 응답 데이터 로그 출력
        this.items = response.data; // 응답 데이터를 직접 items에 할당
        this.filteredItems = response.data; // 필터링된 데이터에 할당
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        this.loading = false;
      }
    },
    updateFilteredItems(filtered) {
      this.filteredItems = filtered;
    },
    editItem(item) {
      this.editedIndex = this.items.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialog = true;
    },
    deleteItem(item) {
      const index = this.items.indexOf(item);
      if (confirm('Are you sure you want to delete this item?')) {
        this.items.splice(index, 1);
      }
    },
    close() {
      this.dialog = false;
      setTimeout(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      }, 300);
    },
    save() {
      if (this.editedIndex > -1) {
        Object.assign(this.items[this.editedIndex], this.editedItem);
      } else {
        this.items.push(this.editedItem);
      }
      this.close();
    },
    reset() {
      this.items = [];
      this.fetchData();
    },
  },
  mounted() {
    this.fetchData();
  },
}
</script>

<style scoped>
/* .search-container {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px; */

/* .filter-container {
} */

.search-container > div {
  flex-direction: row-reverse;
  align-items: right;
  width: 200px !important;
}

.search-container .v-text-field {
  max-width: 300px;
}
</style>
