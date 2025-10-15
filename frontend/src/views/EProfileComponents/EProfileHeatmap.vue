<template>
  <div>
    <!-- 히트맵 데이터가 있을 때만 표시 -->
    <div v-if="hasHeatmapData">
      <!-- Heatmap Legend (상단 우측에 배치) -->
      <div class="heatmap-legend-top">
        <span>Less</span>
        <div class="legend-squares">
          <div class="legend-square level-0"></div>
          <div class="legend-square level-1"></div>
          <div class="legend-square level-2"></div>
          <div class="legend-square level-3"></div>
        </div>
        <span>More</span>
      </div>
      
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
    </div>
    
    <!-- 데이터가 없을 때 표시할 메시지 -->
    <div v-else class="no-data-message">
      <p>활동 데이터가 없습니다.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EProfileHeatmap',
  props: {
    heatmapData: {
      type: Object,
      default: () => ({})
    }
  },
  computed: {
    hasHeatmapData() {
      // heatmapData가 비어있지 않고 실제 데이터가 있는지 확인
      return this.heatmapData && Object.keys(this.heatmapData).length > 0
    },
    weekDays() {
      if (!this.hasHeatmapData) return []
      
      return [
        { day: 'Mon', hours: this.heatmapData.Mon || {} },
        { day: 'Tue', hours: this.heatmapData.Tue || {} },
        { day: 'Wed', hours: this.heatmapData.Wed || {} },
        { day: 'Thu', hours: this.heatmapData.Thu || {} },
        { day: 'Fri', hours: this.heatmapData.Fri || {} },
        { day: 'Sat', hours: this.heatmapData.Sat || {} },
        { day: 'Sun', hours: this.heatmapData.Sun || {} }
      ]
    }
  },
  methods: {
    getActivityCount(dayData, hour) {
      return dayData.hours[hour - 1] || 0
    },
    getHeatmapCellClass(dayData, hour) {
      const count = this.getActivityCount(dayData, hour)
      return this.getHeatmapLevel(count)
    },
    getHeatmapLevel(count) {
      if (count === 0) return 'level-0'    // 0개
      if (count <= 10) return 'level-1'    // 1 ~ 10개
      if (count <= 20) return 'level-2'    // 11 ~ 20개
      return 'level-3'                     // 21개 이상
    }
  }
}
</script>

<style scoped>
.heatmap-legend-top {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  font-size: 13px;
  color: #616161;
  margin-bottom: 15px;
  margin-top: -30px;
  padding-right: 10px;
}

.heatmap {
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-rows: auto 1fr auto;
  gap: 10px;
  margin-bottom: 30px;
  margin-top: -2px;
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

/* 기존 하단 범례 스타일 제거 (더 이상 사용하지 않음) */

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

.no-data-message {
  text-align: center;
  padding: 40px;
  color: #616161;
  font-size: 16px;
}
</style> 