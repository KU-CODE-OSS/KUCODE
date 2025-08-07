<template>
  <div class="e-portfolio">
    <!-- Save Button -->
      <div class="save-section">
        <button class="save-btn">변경사항 저장</button>
      </div>
      
    <!-- Main Content -->
    <main class="main-content">
      <!-- Profile Section -->
      <section class="profile-section">
        <div class="profile-card">
          <div class="profile-info">
            <h2 class="profile-name">김OO 님</h2>
            <div class="profile-details">
              <div class="detail-item">
                <i class="icon-location"></i>
                <div class="detail-content">
                  <span>고려대학교</span>
                  <span>컴퓨터공학과</span>
                </div>
              </div>
              <div class="detail-item">
                <i class="icon-mail"></i>
                <span>abcde123@korea.ac.kr</span>
              </div>
            </div>
            <button class="edit-profile-btn">프로필 편집</button>
          </div>
        </div>

        <!-- Tech Stack Section -->
        <div class="tech-stack-card">
          <h3 class="section-title">나의 기술 스택</h3>
          <div class="tech-stack-content">
            <!-- Tech Stack Chart -->
            <div class="tech-chart">
              <div class="chart-container">
                <div class="chart-circle">
                  <span class="chart-label">Python</span>
                </div>
              </div>
              <div class="chart-legend">
                <div class="legend-item">
                  <div class="legend-color primary"></div>
                  <span>Python</span>
                </div>
                <div class="legend-item">
                  <div class="legend-color secondary"></div>
                  <span>C++</span>
                </div>
                <div class="legend-item">
                  <div class="legend-color tertiary"></div>
                  <span>기타</span>
                </div>
              </div>
            </div>

            <!-- Tech Lists -->
            <div class="tech-lists">
              <div class="tech-column">
                <h4 class="tech-column-title">주요 사용 언어</h4>
                <div class="tech-tags">
                  <div class="tech-tag">
                    <i class="icon-react"></i>
                    <span>Python</span>
                    <i class="icon-arrow-down"></i>
                  </div>
                  <div class="tech-tag">
                    <i class="icon-python"></i>
                    <span>Python</span>
                    <i class="icon-arrow-down"></i>
                  </div>
                  <div class="tech-tag">
                    <i class="icon-kotlin"></i>
                    <span>Kotlin</span>
                    <i class="icon-arrow-down"></i>
                  </div>
                </div>
              </div>

              <div class="tech-column">
                <h4 class="tech-column-title">주요 기술 스택</h4>
                <div class="tech-tags">
                  <div class="tech-tag">
                    <i class="icon-js"></i>
                    <span>JS</span>
                    <i class="icon-arrow-down"></i>
                  </div>
                  <div class="tech-tag">
                    <i class="icon-django"></i>
                    <span>Django</span>
                    <i class="icon-arrow-down"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Skills Section -->
      <section class="skills-section">
        <div class="section-header">
          <i class="icon-file"></i>
          <h3>세부 역량</h3>
        </div>
        <div class="skills-stats">
          <div class="stat-item">
            <h4>추가 / 삭제 커밋 라인 수</h4>
            <p>1200 / 500</p>
          </div>
          <div class="stat-item">
            <h4>이슈 생성 / 닫은 수</h4>
            <p>45 / 20</p>
          </div>
          <div class="stat-item">
            <h4>PR 생성 수</h4>
            <p>120수</p>
          </div>
          <div class="stat-item">
            <h4>오픈 소스 기여</h4>
            <p>X</p>
          </div>
        </div>
      </section>

      <!-- Activity Section -->
      <section class="activity-section">
        <div class="activity-charts">
          <!-- Activity Trends Chart -->
          <div class="chart-card">
            <div class="chart-header">
              <div class="chart-title">
                <i class="icon-activity"></i>
                <h3>활동 추이</h3>
              </div>
              <div class="chart-toggle">
                <span class="toggle-active">월간</span>
                <span class="toggle-inactive">주간</span>
              </div>
            </div>
            <p class="chart-description">최근 대규모의 커밋량 변동이 많았습니다</p>
            
            <!-- Chart Legend -->
            <div class="chart-legend-horizontal">
              <div class="legend-item">
                <div class="legend-dot" style="background: #C16179;"></div>
                <span>Repos</span>
              </div>
              <div class="legend-item">
                <div class="legend-dot" style="background: #FF176A;"></div>
                <span>Commit</span>
              </div>
              <div class="legend-item">
                <div class="legend-dot" style="background: #FF90AB;"></div>
                <span>Stars</span>
              </div>
            </div>

            <!-- Chart Area (placeholder for chart library) -->
            <div class="chart-area">
              <div class="chart-y-axis">
                <span>80</span>
                <span>70</span>
                <span>60</span>
                <span>50</span>
                <span>40</span>
                <span>30</span>
                <span>20</span>
                <span>10</span>
                <span>0</span>
              </div>
              <div class="chart-content">
                <!-- Chart visualization would go here -->
                <div class="chart-placeholder">Chart visualization area</div>
              </div>
              <div class="chart-x-axis">
                <span>5월</span>
                <span>6월</span>
                <span>7월</span>
                <span>8월</span>
                <span>10월</span>
                <span>11월</span>
                <span>12월</span>
              </div>
            </div>
          </div>

          <!-- Project Team Size Chart -->
          <div class="chart-card">
            <div class="chart-header">
              <h3>활동 프로젝트 인원 비율</h3>
            </div>
            <p class="chart-description">2인 프로젝트 인원 비율이 가장 높습니다</p>
            
            <!-- Bar Chart Area -->
            <div class="bar-chart">
              <div class="bar-chart-content">
                <!-- Chart visualization would go here -->
                <div class="chart-placeholder">Bar chart visualization area</div>
              </div>
              <div class="bar-chart-labels">
                <span>1인</span>
                <span>2인</span>
                <span>3인</span>
                <span>4인</span>
                <span>5인 이상</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Activity Time Pattern -->
        <div class="time-pattern-card">
          <div class="section-header">
            <i class="icon-activity"></i>
            <h3>활동 시간대</h3>
          </div>
          
          <!-- 히트맵 컴포넌트 -->
          <EProfileHeatmap :heatmapData="heatmapData" />
        </div>
      </section>

      <!-- Projects Section -->
      <section class="projects-section">
        <div class="section-header">
          <i class="icon-archive"></i>
          <h3>나의 프로젝트</h3>
        </div>
        
        <!-- Projects Table -->
        <div class="projects-table">
          <div class="table-header">
            <span>Category</span>
            <span>Repository</span>
            <span>Stars</span>
            <span>Forks</span>
            <span>Commits</span>
            <span>PRs</span>
            <span>Issues</span>
            <span>Watchers</span>
            <span>Language</span>
            <span>Contribution</span>
            <span>기여학생</span>
          </div>
          
          <div class="table-row">
            <div class="category-tag autonomous">자율</div>
            <span>tensorflow</span>
            <span>181023</span>
            <span>컴퓨터학과</span>
            <span>1517192</span>
            <span>23550</span>
            <span>38455</span>
            <span>7657</span>
            <span>C++</span>
            <span>3474</span>
            <span><i class="icon-link"></i></span>
          </div>
          
          <div class="table-row">
            <div class="category-tag course">컴퓨터프로..</div>
            <span>tensorflow</span>
            <span>181023</span>
            <span>컴퓨터학과</span>
            <span>1517192</span>
            <span>23550</span>
            <span>38455</span>
            <span>7657</span>
            <span>C++</span>
            <span>3474</span>
            <span><i class="icon-link"></i></span>
          </div>
          
          <div class="table-row">
            <div class="category-tag course">알고리즘</div>
            <span>tensorflow</span>
            <span>181023</span>
            <span>컴퓨터학과</span>
            <span>1517192</span>
            <span>23550</span>
            <span>38455</span>
            <span>7657</span>
            <span>C++</span>
            <span>3474</span>
            <span><i class="icon-link"></i></span>
          </div>
        </div>
      </section>

    </main>
  </div>
</template>

<script>
import EProfileHeatmap from './EProfileComponents/EProfileHeatmap.vue'

export default {
  name: 'EPortfolioDashboard',
  components: {
    EProfileHeatmap
  },
  data() {
    return {
      user: {
        name: '김OO',
        university: '고려대학교',
        department: '컴퓨터공학과',
        email: 'abcde123@korea.ac.kr'
      },
      techStack: {
        languages: ['Python', 'C++', 'JavaScript'],
        frameworks: ['Django', 'React', 'Vue.js']
      },
      stats: {
        commitLines: { added: 1200, deleted: 500 },
        issues: { created: 45, closed: 20 },
        pullRequests: 120,
        openSourceContributions: 0
      },
      // 히트맵 데이터
      heatmapData: {
        Mon: {
          "0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0,
          "10": 20, "11": 20, "12": 20, "13": 20, "14": 20,
          "15": 5, "16": 5, "17": 5,
          "18": 0, "19": 0, "20": 0, "21": 0, "22": 0, "23": 0
        },
        Tue: {
          "0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0,
          "10": 20, "11": 20, "12": 20, "13": 20, "14": 20,
          "15": 5, "16": 5, "17": 5,
          "18": 0, "19": 0, "20": 0, "21": 0, "22": 0, "23": 0
        },
        Wed: {
          "0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0,
          "10": 20, "11": 20, "12": 20, "13": 20, "14": 20,
          "15": 5, "16": 5, "17": 5,
          "18": 0, "19": 0, "20": 0, "21": 0, "22": 0, "23": 0
        },
        Thu: {
          "0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0,
          "10": 20, "11": 20, "12": 20, "13": 20, "14": 20,
          "15": 5, "16": 5, "17": 5,
          "18": 0, "19": 0, "20": 0, "21": 0, "22": 0, "23": 0
        },
        Fri: {
          "0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0,
          "10": 20, "11": 20, "12": 20, "13": 20, "14": 20,
          "15": 5, "16": 5, "17": 5,
          "18": 0, "19": 0, "20": 0, "21": 0, "22": 0, "23": 0
        },
        Sat: {
          "0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0,
          "10": 20, "11": 20, "12": 20, "13": 20, "14": 20,
          "15": 5, "16": 5, "17": 5,
          "18": 0, "19": 0, "20": 0, "21": 0, "22": 0, "23": 0
        },
        Sun: {
          "0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0,
          "10": 20, "11": 20, "12": 20, "13": 20, "14": 20,
          "15": 5, "16": 5, "17": 5,
          "18": 0, "19": 0, "20": 0, "21": 0, "22": 0, "23": 0
        }
      }
    }
  },
  methods: {
    editProfile() {
      // Handle profile editing
      console.log('Edit profile clicked');
    },
    saveChanges() {
      // Handle saving changes
      console.log('Save changes clicked');
    }
  }
}
</script>

<style scoped>
/* Global Styles */
.e-portfolio {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #FFFFFF;
  min-height: 100vh;
  width: 1920px;
  margin: 0 auto;
  padding-top: 150px; /* Proper spacing from navigation bar */
}

/* Save Section */
.save-section {
  display: flex;
  justify-content: flex-end;
  padding: 0 320px; /* Align with content area */
  margin-bottom: 30px; /* Space before main content */
}

.save-btn {
  background: #FCFCFC;
  border: 1px solid #CB385C;
  border-radius: 30px;
  padding: 5px 17px;
  font-size: 14px;
  color: #CB385C;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 113px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.save-btn:hover {
  background: #CB385C;
  color: #FCFCFC;
}

/* Main Content */
.main-content {
  width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Profile Section */
.profile-section {
  display: grid;
  grid-template-columns: 415px 848px;
  gap: 16px;
  margin-bottom: 40px;
}

.profile-card,
.tech-stack-card {
  background: #FAFBFD;
  border: 1px solid #E8EDF8;
  border-radius: 20px;
  padding: 30px;
  height: 280px;
}

.profile-name {
  font-size: 26px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 20px 0;
}

.profile-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 30px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 16px;
  color: #262626;
}

.detail-content {
  display: flex;
  gap: 20px;
}

.edit-profile-btn {
  background: #FFFFFF;
  border: 1px solid #CDCDCD;
  border-radius: 10px;
  padding: 15px 126px;
  font-size: 18px;
  color: #616161;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-profile-btn:hover {
  border-color: #910024;
  color: #910024;
}

/* Tech Stack */
/* .tech-stack-card{
    width: 848px;
    height: 280px;
    display: block;
} */

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 20px 0;
}

.tech-stack-content {
  display: block flex;
  gap: 50px;
  align-items: flex-start;
}

.tech-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.chart-container {
  position: relative;
  width: 120px;
  height: 120px;
}

.chart-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF176A 0%, #FFA9BF  50%, #FFDCE5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FF176A;
  font-weight: 500;
}

.chart-legend {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #616161;
}

.legend-color {
  width: 13px;
  height: 13px;
  border-radius: 50%;
}

.legend-color.primary { background: #FF176A; }
.legend-color.secondary { background: #FF84A3; }
.legend-color.tertiary { background: #FFD1DC; }

.tech-lists {
  display: flex;
  flex-direction: column;
  gap: 30px;
  flex: 1;
}

.tech-column-title {
  font-size: 16px;
  font-weight: 600;
  color: #616161;
  margin: 0 0 20px 0;
}

.tech-tags {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.tech-tag {
  background: #EFF2F9;
  border-radius: 10px;
  padding: 5px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  color: #616161;
  max-width: 192px;
}

/* Skills Section */
.skills-section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 30px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.skills-stats {
  background: #FAFBFD;
  border-radius: 10px;
  padding: 30px 40px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 52px;
  text-align: center;
  height: 130px;
  align-items: center;
}

.stat-item {
  border-right: 1px solid #E8EDF8;
}

.stat-item:last-child {
  border-right: none;
}

.stat-item h4 {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 20px 0;
}

.stat-item p {
  font-size: 16px;
  color: #616161;
  margin: 0;
}

/* Activity Section */
.activity-section {
  margin-bottom: 40px;
}

.activity-charts {
  display: grid;
  grid-template-columns: 632px 632px;
  gap: 16px;
  margin-bottom: 30px;
}

.chart-card {
  background: #FFFBFB;
  border-radius: 20px;
  padding: 30px 40px;
  height: 347px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chart-title h3 {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.chart-toggle {
  background: #FFEEF0;
  border-radius: 40px;
  padding: 3px;
  display: flex;
  font-size: 12px;
}

.toggle-active {
  background: #FCFCFC;
  border: 1px solid #FFE2E5;
  border-radius: 42px;
  padding: 5px 15px;
  color: #CB385C;
}

.toggle-inactive {
  padding: 5px 15px;
  color: #FFA7AF;
}

.chart-description {
  font-size: 16px;
  color: #616161;
  margin: 0 0 24px 0;
}

.chart-legend-horizontal {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.chart-area,
.bar-chart {
  height: 200px;
  display: flex;
  flex-direction: column;
}

.chart-placeholder {
  flex: 1;
  background: #f8f9fa;
  border: 2px dashed #dee2e6;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  border-radius: 8px;
}

.chart-y-axis {
  display: flex;
  flex-direction: column-reverse;
  justify-content: space-between;
  height: 100%;
  font-size: 12px;
  color: #262626;
  margin-right: 10px;
}

.chart-x-axis,
.bar-chart-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 14px;
  color: #262626;
}

/* Time Pattern */
.time-pattern-card {
  background: #FFFBFB;
  border-radius: 20px;
  padding: 30px 40px;
  width: 1280px;
  height: 304px;
}

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

.heatmap-placeholder {
  width: 100%;
  height: 100%;
  background: #f8f9fa;
  border: 2px dashed #dee2e6;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  border-radius: 8px;
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

/* Projects Section */
.projects-section {
  margin-bottom: 40px;
}

.projects-table {
  background: #FFFFFF;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  width: 1280px;
}

.table-header {
  background: #F8F9FA;
  display: grid;
  grid-template-columns: repeat(11, 1fr);
  gap: 18px;
  padding: 15px 20px;
  font-size: 16px;
  font-weight: 600;
  color: #CB385C;
  border-bottom: 1px solid #F9D2D6;
}

.table-row {
  display: grid;
  grid-template-columns: repeat(11, 1fr);
  gap: 18px;
  padding: 12px 20px;
  align-items: center;
  border-bottom: 1px solid #DCE2ED;
  font-size: 16px;
  color: #262626;
}

.table-row:last-child {
  border-bottom: none;
}

.category-tag {
  padding: 4px 21px;
  border-radius: 10px;
  font-size: 14px;
  text-align: center;
  max-width: 100px;
}

.category-tag.autonomous {
  background: #EFF2F9;
  color: #507199;
}

.category-tag.course {
  background: #FFEAEC;
  color: #CB385C;
}

/* Icons - You'll need to replace these with actual icon implementations */
.icon-location,
.icon-mail,
.icon-file,
.icon-activity,
.icon-archive,
.icon-link,
.icon-react,
.icon-python,
.icon-kotlin,
.icon-js,
.icon-django,
.icon-arrow-down {
  width: 18px;
  height: 18px;
  background: #949494;
  border-radius: 2px;
}

/* Responsive Design */
@media (max-width: 1920px) {
  .e-portfolio {
    width: 100%;
    max-width: 1920px;
  }
  
  .save-section {
    padding: 0 calc((100% - 1280px) / 2);
  }
  
  .time-pattern-card,
  .projects-table {
    width: 100%;
    max-width: 1280px;
  }
}

@media (max-width: 1400px) {
  .profile-section {
    grid-template-columns: 1fr;
  }
  
  .activity-charts {
    grid-template-columns: 1fr;
  }
  
  .skills-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .table-header,
  .table-row {
    grid-template-columns: repeat(6, 1fr);
    font-size: 14px;
  }
}

@media (max-width: 768px) {
  .e-portfolio {
    padding-top: 100px;
  }
  
  .main-content {
    width: 100%;
    padding: 0 15px;
  }
  
  .save-section {
    padding: 0 15px;
  }
  
  .tech-stack-content {
    flex-direction: column;
    align-items: center;
  }
  
  .skills-stats {
    grid-template-columns: 1fr;
  }
  
  .heatmap-x-labels {
    grid-template-columns: repeat(12, 1fr);
    font-size: 10px;
  }
}
</style>