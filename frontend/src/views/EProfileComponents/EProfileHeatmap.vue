<template>
  <div>
    <!-- Heatmap -->
    <div class="heatmap">
      <div class="heatmap-y-labels">
        <span>월</span>
        <span>화</span>
        <span>수</span>
        <span>목</span>
        <span>금</span>
        <span>토</span>
        <span>일</span>
      </div>
      <div class="heatmap-content">
        <!-- 실제 히트맵 그리드 생성 -->
        <div class="heatmap-grid">
          <div 
            v-for="(dayData, dayIndex) in weekDays" 
            :key="dayIndex"
            class="heatmap-row"
          >
            <div 
              v-for="hour in 24" 
              :key="hour"
              :class="getHeatmapCellClass(dayData, hour)"
              class="heatmap-cell"
              :title="`${dayData.day} ${hour-1}시: ${getActivityCount(dayData, hour)}개`"
            ></div>
          </div>
        </div>
      </div>
      <div class="heatmap-x-labels">
        <span v-for="hour in 24" :key="hour">{{ hour - 1 }}</span>
      </div>
    </div>
    
    <!-- Heatmap Legend -->
    <div class="heatmap-legend">
      <span>Less</span>
      <div class="legend-squares">
        <div class="legend-square level-0"></div>
        <div class="legend-square level-1"></div>
        <div class="legend-square level-2"></div>
        <div class="legend-square level-3"></div>
      </div>
      <span>More</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EProfileHeatmap',
  props: {
    heatmapData: {
      type: Object,
      default: () => ({
        Mon: 0,
        Tue: 0,
        Wed: 0,
        Thu: 0,
        Fri: 0,
        Sat: 0,
        Sun: 0
      })
    }
  },
  data() {
    return {
      weekDays: [
        { day: 'Mon', hours: this.generateHourData() },
        { day: 'Tue', hours: this.generateHourData() },
        { day: 'Wed', hours: this.generateHourData() },
        { day: 'Thu', hours: this.generateHourData() },
        { day: 'Fri', hours: this.generateHourData() },
        { day: 'Sat', hours: this.generateHourData() },
        { day: 'Sun', hours: this.generateHourData() }
      ]
    }
  },
  methods: {
    generateHourData() {
      const hours = {}
      for (let hour = 0; hour < 24; hour++) {
        // 10시-15시: 20개, 15시-18시: 5개, 나머지: 0개
        if (hour >= 10 && hour < 15) {
          hours[hour] = 20
        } else if (hour >= 15 && hour < 18) {
          hours[hour] = 5
        } else {
          hours[hour] = 0
        }
      }
      return hours
    },
    getActivityCount(dayData, hour) {
      return dayData.hours[hour - 1] || 0
    },
    getHeatmapCellClass(dayData, hour) {
      const count = this.getActivityCount(dayData, hour)
      return this.getHeatmapLevel(count)
    },
    getHeatmapLevel(count) {
      if (count === 0) return 'level-0'
      if (count <= 3) return 'level-1'
      if (count <= 10) return 'level-2'
      return 'level-3'
    }
  }
}
</script>

<style scoped>
.heatmap {
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-rows: auto 1fr auto;
  gap: 10px;
  margin: 30px 0;
}

.heatmap-y-labels {
  grid-column: 1;
  grid-row: 2;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 12px;
  color: #262626;
}

.heatmap-content {
  grid-column: 2;
  grid-row: 2;
  background: #FFFFFF;
  border: 1px solid #F9D2D6;
  border-radius: 11px;
  padding: 11px;
  min-height: 155px;
}

.heatmap-grid {
  display: grid;
  grid-template-rows: repeat(7, 1fr);
  gap: 2px;
  height: 100%;
}

.heatmap-row {
  display: grid;
  grid-template-columns: repeat(24, 1fr);
  gap: 1px;
}

.heatmap-cell {
  width: 100%;
  height: 100%;
  border-radius: 2px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.heatmap-cell:hover {
  opacity: 0.8;
}

.heatmap-x-labels {
  grid-column: 2;
  grid-row: 3;
  display: grid;
  grid-template-columns: repeat(24, 1fr);
  gap: 5px;
  font-size: 12px;
  color: #262626;
  text-align: center;
}

.heatmap-legend {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  font-size: 13px;
  color: #616161;
}

.legend-squares {
  display: flex;
  gap: 2px;
}

.legend-square {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.level-0 { background: rgba(89, 115, 147, 0.04); }
.level-1 { background: #FFD1DC; }
.level-2 { background: #FF84A3; }
.level-3 { background: #FF176A; }
</style> 