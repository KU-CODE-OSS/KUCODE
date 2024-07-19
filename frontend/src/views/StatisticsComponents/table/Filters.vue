<template>
  <v-container class="filter_box" >
    <v-row>
      <v-col cols="12">
        <v-combobox
          v-model="yearFilters"
          :items="[2024, 2023, 2022, 2021]"
          label="연도"
          @update:modelValue="applyFilter"
          chips
          multiple
          prepend-icon="mdi-calendar" 
          clearable
        ></v-combobox>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-combobox
          v-model="departmentFilters"
          :items="[...new Set(students.map(student => student.department))]"
          label="학과"
          @update:modelValue="applyFilter"
          chips
          multiple
          prepend-icon="mdi-school"
          clearable
        ></v-combobox>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-combobox
          v-model="courseFilters"
          :items="[...new Set(students.map(student => student.course_name))]"
          label="과목"
          @update:modelValue="applyFilter"
          chips
          multiple
          prepend-icon="mdi-book-education-outline"
          clearable
        ></v-combobox>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  props: {
    students: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      yearFilters: [],
      departmentFilters: [],
      courseFilters: [],
    }
  },
  methods: {
    applyFilter() {
      let filtered = this.students

      if (this.yearFilters.length > 0) {
        filtered = filtered.filter(student =>
          this.yearFilters.includes(student.year)
        )
      }

      if (this.departmentFilters.length > 0) {
        filtered = filtered.filter(student =>
          this.departmentFilters.includes(student.department)
        )
      }

      if (this.courseFilters.length > 0) {
        filtered = filtered.filter(student =>
          this.courseFilters.includes(student.course_name)
        )
      }

      this.$emit('update:filteredStudents', filtered)
    },
  },
  watch: {
    students: {
      handler(newStudents) {
        this.applyFilter()
      },
      deep: true,
    },
  },
  created() {
    this.applyFilter()
  },
}
</script>

<style scoped>
.filter_box {
  max-width: 400px;
  width: 300px;
  /* margin-top: 0 auto; */
  /* align-content: center; */
}
</style>
