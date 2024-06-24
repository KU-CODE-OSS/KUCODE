<template>
    <v-expansion-panels>
      <v-expansion-panel>
        <v-expansion-panel-title>연도</v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-checkbox
            v-for="year in years"
            :key="year"
            :value="year"
            :label="year"
            :model-value="localSelectedYears"
            @update:model-value="updateSelectedYears"
          ></v-checkbox>
        </v-expansion-panel-text>
      </v-expansion-panel>
      <!-- Add more filters here -->
    </v-expansion-panels>
  </template>
  
  <script>
  export default {
    props: {
      years: {
        type: Array,
        required: true
      },
      selectedYears: {
        type: Array,
        required: true
      }
    },
    data() {
      return {
        localSelectedYears: this.selectedYears
      };
    },
    methods: {
      updateSelectedYears(value) {
        this.localSelectedYears = value;
        this.$emit('update:selectedYears', value);
      }
    },
    watch: {
      selectedYears(newVal) {
        this.localSelectedYears = newVal;
      }
    }
  }
  </script>
  