<template>
  <div class="board-page">
    <div class="board-container">
      <!-- Left Sidebar Navigation -->
      <aside class="sidebar-navigation">
        <button
          v-for="category in categories"
          :key="category.value"
          class="sidebar-nav-item"
          :class="{ active: activeCategory === category.value }"
          @click="selectCategory(category.value)"
        >
          <span>{{ category.label }}</span>
          <svg v-if="activeCategory === category.value" width="12" height="8" viewBox="0 0 12 8" fill="none" class="arrow-icon">
            <path d="M1 1L6 6L11 1" stroke="#CB385C" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </aside>

      <!-- Main Content Area -->
      <main class="main-content">
        <div class="content-header">
          <h1 class="page-title">{{ activeCategoryLabel }}</h1>

          <div class="header-actions">
            <div v-if="activeCategory === 'opensource'" class="notice-navigation">
              <button
                v-for="tab in noticeTabs"
                :key="tab.value"
                class="notice-tab"
                :class="{ active: activeNoticeTab === tab.value }"
                @click="activeNoticeTab = tab.value"
              >
                {{ tab.label }}
              </button>
            </div>

            <div class="filter-dropdown" @click="toggleYearDropdown">
              <span>{{ selectedYear }}년</span>
              <svg width="12" height="8" viewBox="0 0 12 8" fill="none" class="dropdown-icon">
                <path d="M1 1.5L6 6.5L11 1.5" stroke="#616161" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <div v-if="showYearDropdown" class="dropdown-menu">
                <div
                  v-for="year in availableYears"
                  :key="year"
                  class="dropdown-option"
                  @click.stop="selectYear(year)"
                >
                  {{ year }}년
                </div>
              </div>
            </div>

            <button
              class="write-post-btn"
              @click="openWritePost"
              :disabled="activeCategory === 'opensource'"
              :class="{ disabled: activeCategory === 'opensource' }"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" class="btn-icon">
                <circle cx="10" cy="10" r="9.25" stroke="#616161" stroke-width="1.5"/>
                <path d="M10 6V14M6 10H14" stroke="#616161" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              글 작성
            </button>

            <div class="search-container">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" class="search-icon">
                <circle cx="9" cy="9" r="5.75" stroke="#616161" stroke-width="1.5"/>
                <path d="M13 13L16 16" stroke="#616161" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </div>
          </div>
        </div>

        <div class="content-meta">
          <span class="total-count">총 {{ filteredPosts.length }}건</span>
        </div>

        <!-- Posts Table -->
        <div class="posts-table">
          <!-- Event Information & Learning Materials Table -->
          <div v-if="activeCategory !== 'opensource'" class="table-wrapper">
            <div class="table-header">
              <div class="table-row header-row">
                <div class="table-cell col-number">번호</div>
                <div class="table-cell col-title">제목</div>
                <div class="table-cell col-date">등록 일자</div>
                <div class="table-cell col-author">작성자</div>
                <div class="table-cell col-views">조회수</div>
              </div>
            </div>

            <div class="table-body">
              <div
                v-for="post in filteredPosts"
                :key="post.id"
                class="table-row"
                @click="openPost(post.id)"
              >
                <div class="table-cell col-number">{{ post.number }}</div>
                <div class="table-cell col-title">{{ post.title }}</div>
                <div class="table-cell col-date">{{ post.date }}</div>
                <div class="table-cell col-author">{{ post.author }}</div>
                <div class="table-cell col-views">{{ post.views }}</div>
              </div>
            </div>
          </div>

          <!-- Open Source Repos Table -->
          <div v-else class="table-wrapper">
            <div class="table-header">
              <div class="table-row header-row repos-header">
                <div class="table-cell col-repos-number">순번</div>
                <div class="table-cell col-repos-company">기업 명</div>
                <div class="table-cell col-repos-count">저장소 개수</div>
                <div class="table-cell col-repos-followers">팔로워 수</div>
                <div class="table-cell col-repos-url">Github 주소</div>
              </div>
            </div>

            <div class="table-body">
              <div
                v-for="repo in filteredRepos"
                :key="repo.id"
                class="table-row"
              >
                <div class="table-cell col-repos-number">{{ repo.number }}</div>
                <div class="table-cell col-repos-company">{{ repo.company }}</div>
                <div class="table-cell col-repos-count">{{ repo.repoCount }}</div>
                <div class="table-cell col-repos-followers">{{ repo.followers }}</div>
                <div class="table-cell col-repos-url">
                  <a :href="repo.url" target="_blank" class="github-link">{{ repo.url }}</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BoardPage',
  data() {
    return {
      categories: [
        { label: '행사 정보', value: 'events' },
        { label: '학습 자료', value: 'learning' },
        { label: '오픈소스 Repos', value: 'opensource' }
      ],
      noticeTabs: [
        { label: '행사 정보', value: 'events' },
        { label: '학생', value: 'student' }
      ],
      activeCategory: 'events',
      activeNoticeTab: 'events',
      selectedYear: 2025,
      showYearDropdown: false,
      availableYears: [2025, 2024, 2023, 2022, 2021, 2020],
      eventPosts: [
        { id: 1, number: '1', title: '주제', date: '2025.11.15', author: '김OO', views: '1234', category: 'events' },
        { id: 2, number: '2', title: '주제', date: '2025.11.15', author: '김OO', views: '1234', category: 'events' },
        { id: 3, number: '3', title: '주제', date: '2025.11.15', author: '김OO', views: '1234', category: 'events' },
        { id: 4, number: '4', title: '주제', date: '2025.11.15', author: '김OO', views: '1234', category: 'events' },
        { id: 5, number: '5', title: '주제', date: '2025.11.15', author: '김OO', views: '1234', category: 'events' },
        { id: 6, number: '6', title: '주제', date: '2025.11.15', author: '김OO', views: '1234', category: 'events' },
        { id: 7, number: '7', title: '주제', date: '2025.11.15', author: '김OO', views: '1234', category: 'events' }
      ],
      learningPosts: [
        { id: 1, number: '1', title: 'Git의 기초 및 Git을 이용한 프로젝트 형상관리 방법', date: '2025.10.16', author: '황영숙', views: '1234', category: 'learning' },
        { id: 2, number: '2', title: '도커와 컨테이너 기초와 활용', date: '2025.11.15', author: '황영숙', views: '1234', category: 'learning' },
        { id: 3, number: '3', title: 'DevOps - CI/CD 구성하기', date: '2025.10.16', author: '황영숙', views: '1234', category: 'learning' },
        { id: 4, number: '4', title: 'MLOPs 구축하기', date: '2025.10.16', author: '황영숙', views: '1234', category: 'learning' },
        { id: 5, number: '5', title: '학습 자료 1', date: '2025.10.16', author: '황영숙', views: '1234', category: 'learning' },
        { id: 6, number: '6', title: '학습 자료 2', date: '2025.10.16', author: '황영숙', views: '1234', category: 'learning' },
        { id: 7, number: '7', title: 'Design of Scalable System Architectures', date: '2025.10.16', author: '황영숙', views: '1234', category: 'learning' }
      ],
      repositories: [
        { id: 1, number: '1', company: '티맥스클라우드', repoCount: '271', followers: '57', url: 'https://github.com/tmax-cloud' },
        { id: 2, number: '2', company: '네이버', repoCount: '269', followers: '2377', url: 'https://github.com/naver' },
        { id: 3, number: '3', company: '인베슘', repoCount: '199', followers: '70', url: 'https://github.com/hamonikr' },
        { id: 4, number: '4', company: '삼성전자', repoCount: '182', followers: '1342', url: 'https://github.com/Samsung' },
        { id: 5, number: '5', company: '샌드버드', repoCount: '194', followers: '340', url: 'https://github.com/sendbird' },
        { id: 6, number: '6', company: '데브시스터즈', repoCount: '178', followers: '248', url: 'https://github.com/devsisters' },
        { id: 7, number: '7', company: '리디', repoCount: '114', followers: '167', url: 'https://github.com/ridi' },
        { id: 8, number: '8', company: '라인', repoCount: '158', followers: '1304', url: 'https://github.com/line' },
        { id: 9, number: '9', company: '당근마켓', repoCount: '120', followers: '1143', url: 'https://github.com/daangn' }
      ]
    }
  },
  computed: {
    activeCategoryLabel() {
      const category = this.categories.find(cat => cat.value === this.activeCategory)
      return category ? category.label : ''
    },
    filteredPosts() {
      if (this.activeCategory === 'events') {
        return this.eventPosts
      } else if (this.activeCategory === 'learning') {
        return this.learningPosts
      }
      return []
    },
    filteredRepos() {
      return this.repositories
    }
  },
  methods: {
    selectCategory(categoryValue) {
      this.activeCategory = categoryValue
      // Update URL query to preserve category state
      this.$router.replace({ path: '/board', query: { category: categoryValue } })
    },
    toggleYearDropdown() {
      this.showYearDropdown = !this.showYearDropdown
    },
    selectYear(year) {
      this.selectedYear = year
      this.showYearDropdown = false
    },
    openWritePost() {
      // Navigate to appropriate create form based on active category
      if (this.activeCategory === 'events') {
        this.$router.push({ path: '/board/event/create', query: { from: this.activeCategory } })
      } else if (this.activeCategory === 'learning') {
        this.$router.push({ path: '/board/materials/create', query: { from: this.activeCategory } })
      }
      // opensource category doesn't have create functionality
    },
    openPost(postId) {
      // Both events and learning materials have detail views
      if (this.activeCategory === 'events') {
        this.$router.push({ path: `/board/event/${postId}`, query: { from: this.activeCategory } })
      } else if (this.activeCategory === 'learning') {
        this.$router.push({ path: `/board/materials/${postId}`, query: { from: this.activeCategory } })
      }
    },
    restoreCategoryFromQuery() {
      // Restore category from query parameter if present
      const categoryFromQuery = this.$route.query.category
      if (categoryFromQuery && ['events', 'learning', 'opensource'].includes(categoryFromQuery)) {
        this.activeCategory = categoryFromQuery
      }
    }
  },
  mounted() {
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.filter-dropdown')) {
        this.showYearDropdown = false
      }
    })
    // Restore category state when component mounts
    this.restoreCategoryFromQuery()
  },
  watch: {
    '$route.query.category': function(newCategory) {
      if (newCategory && ['events', 'learning', 'opensource'].includes(newCategory)) {
        this.activeCategory = newCategory
      }
    }
  }
}
</script>

<style scoped>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

.board-page {
  width: 100%;
  min-height: 100vh;
  background: #FFFFFF;
  font-family: 'Pretendard', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #262626;
  padding-top: 120px;
  display: flex;
  justify-content: center;
}

.board-container {
  width: 1920px;
  max-width: 100%;
  display: flex;
  position: relative;
}

/* Sidebar Navigation */
.sidebar-navigation {
  width: 268px;
  padding: 155px 0 0 0;
  margin-left: 320px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 18px;
  background: #FFFFFF;
  flex-shrink: 0;
}

.sidebar-nav-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-family: 'Pretendard', sans-serif;
  font-weight: 600;
  font-size: 18px;
  line-height: 21px;
  color: #949494;
  background: transparent;
  border: none;
  padding: 12px 24px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 8px;
}

.sidebar-nav-item:hover {
  background: #FFFBFB;
}

.sidebar-nav-item.active {
  color: #CB385C;
  background: #FFFBFB;
}

.arrow-icon {
  flex-shrink: 0;
}

/* Main Content */
.main-content {
  flex: 1;
  max-width: 1012px;
  padding: 71px 40px 40px;
  border-left: 1px solid #DCE2ED;
  background: #FFFFFF;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-family: 'Pretendard', sans-serif;
  font-weight: 600;
  font-size: 26px;
  line-height: 31px;
  color: #262626;
  margin: 0;
}

/* Header Actions */
.header-actions {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.notice-navigation {
  display: flex;
  gap: 16px;
  margin-right: 20px;
}

.notice-tab {
  font-family: 'Pretendard', sans-serif;
  font-weight: 600;
  font-size: 18px;
  line-height: 21px;
  color: #CDCDCD;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px 12px;
  transition: color 0.2s ease;
}

.notice-tab.active {
  color: #CB385C;
}

.filter-dropdown {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  width: 147px;
  height: 38px;
  box-sizing: border-box;
  background: #FCFCFC;
  border: 1px solid #CDCDCD;
  border-radius: 10px;
  cursor: pointer;
  font-family: 'Pretendard', sans-serif;
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  color: #616161;
}

.dropdown-icon {
  margin-left: auto;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: #FFFFFF;
  border: 1px solid #DCE2ED;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 10;
  overflow: hidden;
}

.dropdown-option {
  padding: 10px 20px;
  font-family: 'Pretendard', sans-serif;
  font-size: 14px;
  color: #616161;
  cursor: pointer;
  transition: background 0.2s ease;
}

.dropdown-option:hover {
  background: #F8F8F8;
}

.write-post-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  width: auto;
  min-width: 88px;
  height: 44px;
  box-sizing: border-box;
  background: #F8F8F8;
  border: none;
  border-radius: 10px;
  font-family: 'Pretendard', sans-serif;
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  color: #616161;
  cursor: pointer;
  transition: all 0.2s ease;
}

.write-post-btn:hover {
  background: #EFEFEF;
}

.write-post-btn.disabled,
.write-post-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.write-post-btn.disabled:hover,
.write-post-btn:disabled:hover {
  background: #F8F8F8;
}

.btn-icon {
  flex-shrink: 0;
}

.search-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: #F8F8F8;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.search-container:hover {
  background: #EFEFEF;
}

.search-icon {
  flex-shrink: 0;
}

.content-meta {
  margin-bottom: 12px;
}

.total-count {
  font-family: 'Pretendard', sans-serif;
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  color: #AEAEAE;
}

/* Posts Table */
.posts-table {
  width: 100%;
  background: #FFFFFF;
}

.table-wrapper {
  width: 100%;
}

.table-header {
  border-top: 1px solid #616161;
}

.table-row {
  display: flex;
  align-items: center;
  padding: 14px 10px;
  gap: 16px;
  border-bottom: 0.5px solid #CDCDCD;
  transition: background 0.2s ease;
}

.table-row:not(.header-row):hover {
  background: #FFFBFB;
  cursor: pointer;
}

.header-row {
  background: transparent;
  font-weight: 600;
  border-bottom: 1px solid #DCE2ED;
}

.table-cell {
  font-family: 'Pretendard', sans-serif;
  font-size: 14px;
  line-height: 17px;
  color: #AEAEAE;
}

.header-row .table-cell {
  font-weight: 600;
  font-size: 16px;
  line-height: 19px;
  color: #949494;
}

.table-row:not(.header-row) .col-title {
  font-weight: 600;
  color: #262626;
}

.table-row:not(.header-row) .col-repos-company {
  font-weight: 600;
  color: #262626;
}

/* Event/Learning Table Columns */
.col-number {
  width: 79px;
  flex-shrink: 0;
  text-align: left;
}

.col-title {
  width: 419px;
  flex-shrink: 0;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

.col-date {
  width: 200px;
  flex-shrink: 0;
  text-align: left;
}

.col-author {
  width: 92px;
  flex-shrink: 0;
  text-align: left;
}

.col-views {
  width: 92px;
  flex-shrink: 0;
  text-align: right;
}

/* Open Source Repos Table Columns */
.col-repos-number {
  width: 95px;
  flex-shrink: 0;
  text-align: left;
}

.col-repos-company {
  width: 336px;
  flex-shrink: 0;
  text-align: left;
}

.col-repos-count {
  width: 148px;
  flex-shrink: 0;
  text-align: left;
}

.col-repos-followers {
  width: 110px;
  flex-shrink: 0;
  text-align: left;
}

.col-repos-url {
  width: 192px;
  flex-shrink: 0;
  text-align: left;
}

.github-link {
  color: #AEAEAE;
  text-decoration: underline;
  font-size: 14px;
  transition: color 0.2s ease;
}

.github-link:hover {
  color: #262626;
}

/* Responsive Design */
@media (max-width: 1920px) {
  .board-container {
    width: 100%;
  }

  .sidebar-navigation {
    margin-left: max(20px, calc((100vw - 1280px) / 2));
  }
}

@media (max-width: 1600px) {
  .sidebar-navigation {
    margin-left: 80px;
  }
}

@media (max-width: 1200px) {
  .sidebar-navigation {
    margin-left: 40px;
    width: 220px;
  }

  .main-content {
    padding: 71px 20px 40px;
  }
}

@media (max-width: 768px) {
  .board-page {
    padding-top: 120px;
  }

  .board-container {
    flex-direction: column;
  }

  .sidebar-navigation {
    width: 100%;
    margin-left: 0;
    padding: 20px;
    flex-direction: row;
    gap: 12px;
    border-bottom: 1px solid #DCE2ED;
  }

  .main-content {
    border-left: none;
    padding: 20px;
  }

  .content-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }

  .col-date,
  .col-author {
    display: none;
  }
}
</style>
