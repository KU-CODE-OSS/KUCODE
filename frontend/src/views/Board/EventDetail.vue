<template>
  <div class="event-detail-page">
    <div class="detail-container">
      <!-- Left Sidebar Navigation -->
      <aside class="sidebar-navigation">
        <button
          v-for="category in categories"
          :key="category.value"
          class="sidebar-nav-item"
          :class="{ active: category.value === 'events' }"
          @click="navigateToCategory(category.value)"
        >
          <span>{{ category.label }}</span>
          <svg v-if="category.value === 'events'" width="12" height="8" viewBox="0 0 12 8" fill="none" class="arrow-icon">
            <path d="M1 1L6 6L11 1" stroke="#CB385C" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </aside>

      <!-- Main Content Area -->
      <main class="main-content">
        <!-- Back Button -->
        <div class="back-button-wrapper">
          <button @click="goBack" class="back-button">
            <svg width="12" height="8" viewBox="0 0 12 8" fill="none" class="back-icon">
              <path d="M1 1L6 6L11 1" stroke="#949494" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>이전</span>
          </button>
        </div>

        <!-- Post Title -->
        <h1 class="post-title">{{ post.title }}</h1>

        <!-- Post Content -->
        <div class="post-content">
          <p>{{ post.content }}</p>
        </div>

        <!-- Attachment Section -->
        <div class="attachment-section" v-if="post.attachment">
          <a :href="post.attachment.url" download class="attachment-link">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" class="download-icon">
              <path d="M17.5 12.5V15.8333C17.5 16.2754 17.3244 16.6993 17.0118 17.0118C16.6993 17.3244 16.2754 17.5 15.8333 17.5H4.16667C3.72464 17.5 3.30072 17.3244 2.98816 17.0118C2.67559 16.6993 2.5 16.2754 2.5 15.8333V12.5" stroke="#262626" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M5.83334 8.33331L10 12.5L14.1667 8.33331" stroke="#262626" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M10 12.5V2.5" stroke="#262626" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="attachment-name">{{ post.attachment.name }}</span>
          </a>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { getBoardPost } from '@/api.js'

export default {
  name: 'EventDetail',
  data() {
    return {
      categories: [
        { value: 'events', label: '행사 정보' },
        { value: 'learning', label: '학습 자료' },
        { value: 'opensource', label: '오픈소스 Repos' }
      ],
      post: {
        id: null,
        title: '',
        content: '',
        attachment: null
      },
      loading: false,
      error: null
    }
  },
  created() {
    this.loadPost()
  },
  methods: {
    async loadPost() {
      const postId = this.$route.params.id
      this.loading = true
      this.error = null

      try {
        const response = await getBoardPost(postId)
        const postData = response.data.post

        this.post = {
          id: postData.id,
          title: postData.title,
          content: postData.content,
          attachment: postData.attachment || null
        }
      } catch (error) {
        console.error('Failed to load post:', error)
        this.error = 'Failed to load post'
        this.post = {
          id: postId,
          title: '게시글을 찾을 수 없습니다',
          content: '요청하신 게시글이 존재하지 않습니다.',
          attachment: null
        }
      } finally {
        this.loading = false
      }
    },
    goBack() {
      // Preserve category state when going back
      this.$router.push({ path: '/board', query: { category: 'events' } })
    },
    navigateToCategory(categoryValue) {
      // Navigate to board with selected category
      this.$router.push({ path: '/board', query: { category: categoryValue } })
    }
  }
}
</script>

<style scoped>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

.event-detail-page {
  width: 100%;
  min-height: 100vh;
  background: #FFFFFF;
  font-family: 'Pretendard', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #262626;
  padding-top: 120px;
  display: flex;
  justify-content: center;
}

.detail-container {
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  display: flex;
  position: relative;
  padding: 0 40px;
  box-sizing: border-box;
}

/* Sidebar Navigation */
.sidebar-navigation {
  width: 268px;
  padding: 155px 0 0 0;
  margin-right: 40px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 18px;
  background: #FFFFFF;
  flex-shrink: 0;
  z-index: 1;
}

.sidebar-nav-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  min-height: 45px;
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
  box-sizing: border-box;
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
  transform: rotate(-90deg);
}

/* Main Content */
.main-content {
  flex: 1;
  min-width: 0;
  padding: 71px 40px 40px 40px;
  border-left: 1px solid #DCE2ED;
  background: #FFFFFF;
  box-sizing: border-box;
  min-height: calc(100vh - 120px);
}

.back-button-wrapper {
  margin-bottom: 32px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 10px;
  background: none;
  border: none;
  cursor: pointer;
  font-family: 'Pretendard', sans-serif;
  font-weight: 400;
  font-size: 16px;
  line-height: 140%;
  color: #949494;
  padding: 0;
  transition: color 0.2s;
}

.back-button:hover {
  color: #616161;
}

.back-icon {
  transform: rotate(90deg);
}

.post-title {
  font-weight: 600;
  font-size: 22px;
  line-height: 26px;
  letter-spacing: -0.004em;
  color: #262626;
  margin: 0 0 96px 0;
}

.post-content {
  margin-bottom: 68px;
  padding-bottom: 60px;
}

.post-content p {
  font-weight: 400;
  font-size: 16px;
  line-height: 140%;
  color: #616161;
  white-space: pre-wrap;
  margin: 0;
}

.attachment-section {
  width: 100%;
  max-width: 972px;
  height: 50px;
  background: #F8F8F8;
  display: flex;
  align-items: center;
  padding: 0 16px;
  box-sizing: border-box;
}

.attachment-link {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  transition: opacity 0.2s;
}

.attachment-link:hover {
  opacity: 0.7;
}

.download-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.attachment-name {
  font-weight: 600;
  font-size: 16px;
  line-height: 19px;
  color: #262626;
}

/* Responsive Design */
@media (max-width: 1440px) {
  .detail-container {
    max-width: 1200px;
  }
}

@media (max-width: 1200px) {
  .detail-container {
    padding: 0 30px;
  }

  .sidebar-navigation {
    width: 220px;
    margin-right: 30px;
  }

  .main-content {
    padding: 71px 30px 40px;
  }
}

@media (max-width: 1024px) {
  .detail-container {
    padding: 0 20px;
  }

  .sidebar-navigation {
    width: 200px;
    margin-right: 20px;
  }

  .main-content {
    padding: 71px 20px 40px;
  }
}

@media (max-width: 768px) {
  .detail-container {
    flex-direction: column;
  }

  .sidebar-navigation {
    width: 100%;
    margin-right: 0;
    padding: 40px;
    flex-direction: row;
    gap: 16px;
    overflow-x: auto;
  }

  .sidebar-nav-item {
    min-width: 120px;
  }

  .main-content {
    border-left: none;
    border-top: 1px solid #DCE2ED;
    padding: 32px 24px;
  }

  .post-title {
    font-size: 20px;
    margin-bottom: 48px;
  }

  .attachment-section {
    padding: 0 12px;
  }

  .attachment-name {
    font-size: 14px;
    word-break: break-word;
  }
}
</style>
