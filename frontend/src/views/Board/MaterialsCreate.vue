<template>
  <div class="materials-create-page">
    <div class="create-container">
      <h1 class="page-title">학습 자료 글 작성</h1>

      <div class="form-divider-top"></div>

      <form @submit.prevent="handleSubmit" class="create-form">
        <!-- 제목 Field -->
        <div class="form-row">
          <label class="form-label">제목</label>
          <div class="form-input-wrapper">
            <input
              v-model="formData.title"
              type="text"
              class="form-input"
              placeholder="제목을 입력해주세요"
              required
            />
          </div>
        </div>

        <!-- 내용 Field -->
        <div class="form-row content-row">
          <label class="form-label">내용</label>
          <div class="form-input-wrapper">
            <textarea
              v-model="formData.content"
              class="form-textarea"
              placeholder="내용을 입력해주세요"
              required
            ></textarea>
          </div>
        </div>

        <div class="form-row">
          <label class="form-label">공동 소유자</label>
          <div class="form-input-wrapper">
            <PostOwnerSelector v-model="formData.ownerIds" :creator-id="authStore.memberId || ''" />
          </div>
        </div>

        <!-- 첨부파일 Field -->
        <div class="form-row">
          <label class="form-label">Google Drive 링크</label>
          <div class="form-input-wrapper">
            <div class="drive-link-section">
              <input
                v-model="formData.driveUrl"
                type="url"
                class="form-input drive-url-input"
                placeholder="공유 가능한 Google Drive 링크를 입력하세요"
              />
              <input
                v-model="formData.fileName"
                type="text"
                class="form-input file-name-input"
                placeholder="표시할 파일 이름 (선택사항)"
              />
            </div>
            <p class="drive-help">파일의 공유 권한은 Google Drive에서 별도로 설정해야 합니다.</p>
          </div>
        </div>

        <div class="form-divider-bottom"></div>

        <!-- Action Buttons -->
        <div class="form-actions">
          <button type="button" @click="handleCancel" class="btn-cancel">
            취소
          </button>
          <button type="submit" class="btn-submit">
            저장하기
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { createOrUpdatePost, linkDriveFile } from '@/api.js'
import PostOwnerSelector from '@/components/PostOwnerSelector.vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'MaterialsCreate',
  components: { PostOwnerSelector },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      formData: {
        title: '',
        content: '',
        fileName: '',
        driveUrl: '',
        author: '', // Will be set from user session or default
        ownerIds: [],
        year: new Date().getFullYear(),
        semester: '1'
      },
      loading: false,
      error: null
    }
  },
  mounted() {
    this.formData.author = this.authStore.memberId || ''
  },
  methods: {
    handleCancel() {
      // Preserve category state when going back
      this.$router.push({ path: '/board', query: { category: 'learning' } })
    },
    async handleSubmit() {
      this.loading = true
      this.error = null

      try {
        const authorId = this.authStore.memberId || this.formData.author
        if (!authorId) {
          throw new Error('작성자 정보를 확인할 수 없습니다.')
        }
        // Prepare post data according to API spec
        const postData = {
          author: authorId,
          owner_ids: this.formData.ownerIds,
          title: this.formData.title,
          content: this.formData.content,
          category: 'LEARNING_MATERIAL',
          year: this.formData.year,
          semester: this.formData.semester,
          is_internal: true
        }

        // Create post first
        const response = await createOrUpdatePost(postData)
        const postId = response.data.post_id
        console.log('Post created:', postId)

        if (this.formData.driveUrl) {
          try {
            await linkDriveFile(postId, this.formData.driveUrl, this.formData.fileName || null)
          } catch (fileError) {
            console.error('Failed to link Drive file:', fileError)
            alert('게시글은 저장되었으나 Google Drive 링크 저장에 실패했습니다.')
          }
        }

        alert('학습 자료가 저장되었습니다.')
        this.$router.push({ path: '/board', query: { category: 'learning' } })
      } catch (error) {
        console.error('Failed to create post:', error)
        this.error = 'Failed to create post'
        alert('게시글 저장에 실패했습니다. 다시 시도해주세요.')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

.materials-create-page {
  width: 100%;
  min-height: 100vh;
  background: #FFFFFF;
  font-family: 'Pretendard', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #262626;
  padding-top: 120px;
  display: flex;
  justify-content: center;
}

.create-container {
  width: 1920px;
  max-width: 100%;
  padding: 0 536px;
  box-sizing: border-box;
}

.page-title {
  margin: 94px 0 42px 0;
  font-weight: 600;
  font-size: 22px;
  line-height: 26px;
  letter-spacing: -0.004em;
  color: #262626;
}

.form-divider-top,
.form-divider-bottom {
  width: 848px;
  height: 0;
  border: 2px solid #949494;
  margin: 0;
}

.form-divider-bottom {
  margin-top: 80px;
  margin-bottom: 25px;
}

.create-form {
  margin-top: 40px;
}

.form-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 30px;
}

.form-row.content-row {
  margin-bottom: 30px;
}

.form-label {
  width: 92px;
  font-weight: 500;
  font-size: 16px;
  line-height: 19px;
  color: #949494;
  padding-top: 11px;
  flex-shrink: 0;
}

.form-input-wrapper {
  flex: 1;
  max-width: 756px;
}

.form-input {
  width: 100%;
  height: 40px;
  background: #FCFCFC;
  border: none;
  border-bottom: 1px solid #CDCDCD;
  padding: 11px 16px;
  box-sizing: border-box;
  font-family: 'Pretendard', sans-serif;
  font-weight: 500;
  font-size: 16px;
  line-height: 19px;
  color: #262626;
}

.form-input::placeholder {
  color: #949494;
}

.form-input:focus {
  outline: none;
  border-bottom-color: #910024;
}

.form-textarea {
  width: 100%;
  height: 350px;
  background: #FCFCFC;
  border: none;
  border-bottom: 1px solid #CDCDCD;
  padding: 12px 16px;
  box-sizing: border-box;
  font-family: 'Pretendard', sans-serif;
  font-weight: 500;
  font-size: 16px;
  line-height: 19px;
  color: #262626;
  resize: none;
}

.form-textarea::placeholder {
  color: #949494;
}

.form-textarea:focus {
  outline: none;
  border-bottom-color: #910024;
}

.drive-link-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.drive-url-input {
  width: 100%;
}

.file-name-input {
  width: 100%;
}

.drive-help {
  margin: 10px 0 0;
  font-size: 14px;
  color: #949494;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 14px;
  margin-top: 25px;
}

.btn-cancel,
.btn-submit {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px 30px;
  border-radius: 20px;
  font-weight: 500;
  font-size: 16px;
  line-height: 19px;
  border: none;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-cancel {
  background: #F8F8F8;
  color: #616161;
}

.btn-cancel:hover {
  opacity: 0.8;
}

.btn-submit {
  background: #CB385C;
  color: #FCFCFC;
}

.btn-submit:hover {
  background: #910024;
}

/* Responsive Design */
@media (max-width: 1920px) {
  .create-container {
    padding: 0 320px;
  }
}

@media (max-width: 1440px) {
  .create-container {
    padding: 0 160px;
  }
}

@media (max-width: 1024px) {
  .create-container {
    padding: 0 80px;
  }
}

@media (max-width: 768px) {
  .create-container {
    padding: 0 40px;
  }

  .form-row {
    flex-direction: column;
  }

  .form-label {
    margin-bottom: 8px;
    padding-top: 0;
  }

  .form-divider-top,
  .form-divider-bottom {
    width: 100%;
  }
}
</style>
