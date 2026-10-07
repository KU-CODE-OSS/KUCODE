<template>
  <div class="qna-detail-page">
    <div class="detail-container">
      <aside class="sidebar-navigation">
        <button
          v-for="category in categories"
          :key="category.value"
          :class="['sidebar-nav-item', { active: category.value === 'qna' }]"
          @click="navigateToCategory(category.value)"
        >
          {{ category.label }}
        </button>
      </aside>

      <main class="main-content">
        <button type="button" class="back-button" @click="goBack">이전</button>

        <div v-if="loading" class="state-message">질문을 불러오는 중입니다.</div>
        <div v-else-if="error" class="state-message error-message">{{ error }}</div>
        <template v-else>
          <h1>{{ post.title }}</h1>
          <div class="post-meta">
            <span>{{ post.author }}</span>
            <span v-if="post.owners.length">소유자: {{ ownerNames }}</span>
          </div>
          <p class="post-content">{{ post.content }}</p>
          <PostComments v-if="post.id" :post-id="post.id" response-label="답변" />
        </template>
      </main>
    </div>
  </div>
</template>

<script>
import { getBoardPost } from '@/api.js'
import PostComments from '@/components/PostComments.vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'QnaDetail',
  components: { PostComments },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      categories: [
        { value: 'events', label: '행사 정보' },
        { value: 'learning', label: '학습 자료' },
        { value: 'opensource', label: '오픈소스 Repos' },
        { value: 'qna', label: 'Q&A' }
      ],
      post: {
        id: null,
        title: '',
        content: '',
        author: '',
        owners: []
      },
      loading: false,
      error: ''
    }
  },
  computed: {
    ownerNames() {
      return this.post.owners.map(owner => owner.name || owner.id).join(', ')
    }
  },
  created() {
    this.loadPost()
  },
  methods: {
    async loadPost() {
      this.loading = true
      this.error = ''
      try {
        const response = await getBoardPost(this.$route.params.id, this.authStore.memberId)
        const post = response.data.post
        if (post.category !== 'QNA') {
          throw new Error('Requested post is not a Q&A post')
        }
        this.post = {
          id: post.id,
          title: post.title,
          content: post.content,
          author: post.author,
          owners: post.owners || []
        }
      } catch (error) {
        console.error('Failed to load Q&A post:', error)
        this.error = '질문을 불러오지 못했습니다.'
      } finally {
        this.loading = false
      }
    },
    goBack() {
      this.$router.push({ path: '/board', query: { category: 'qna' } })
    },
    navigateToCategory(category) {
      this.$router.push({ path: '/board', query: { category } })
    }
  }
}
</script>

<style scoped>
.qna-detail-page {
  min-height: 100vh;
  padding-top: 120px;
  background: #fff;
  color: #262626;
}

.detail-container {
  display: flex;
  width: min(1360px, calc(100% - 48px));
  margin: 0 auto;
}

.sidebar-navigation {
  display: flex;
  flex: 0 0 268px;
  flex-direction: column;
  gap: 18px;
  padding-top: 155px;
}

.sidebar-nav-item {
  padding: 12px 24px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: #949494;
  font-size: 18px;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
}

.sidebar-nav-item.active {
  background: #fffbfb;
  color: #cb385c;
}

.main-content {
  flex: 1;
  min-height: calc(100vh - 120px);
  padding: 72px 40px;
  border-left: 1px solid #dce2ed;
}

.back-button {
  border: 0;
  background: transparent;
  color: #949494;
  cursor: pointer;
}

h1 {
  margin: 36px 0 12px;
  font-size: 24px;
}

.post-meta {
  display: flex;
  gap: 20px;
  padding-bottom: 24px;
  border-bottom: 1px solid #eef1f5;
  color: #949494;
  font-size: 13px;
}

.post-content {
  min-height: 180px;
  margin: 0;
  padding: 40px 0;
  color: #616161;
  line-height: 1.7;
  white-space: pre-wrap;
}

.state-message {
  padding: 80px 0;
  color: #949494;
}

.error-message {
  color: #b42318;
}

@media (max-width: 820px) {
  .sidebar-navigation {
    display: none;
  }

  .main-content {
    padding: 48px 0;
    border-left: 0;
  }
}
</style>
