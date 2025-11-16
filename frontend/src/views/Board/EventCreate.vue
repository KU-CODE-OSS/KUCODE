<template>
  <div class="event-create-page">
    <div class="create-container">
      <h1 class="page-title">행사정보 글 작성</h1>

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

        <!-- 첨부파일 Field -->
        <div class="form-row">
          <label class="form-label">첨부파일</label>
          <div class="form-input-wrapper file-input-wrapper">
            <div class="file-input-content">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" class="file-icon">
                <path d="M11.6667 1.66669H5.00001C4.55798 1.66669 4.13406 1.84228 3.82149 2.15484C3.50893 2.4674 3.33334 2.89133 3.33334 3.33335V16.6667C3.33334 17.1087 3.50893 17.5326 3.82149 17.8452C4.13406 18.1578 4.55798 18.3334 5.00001 18.3334H15C15.442 18.3334 15.866 18.1578 16.1785 17.8452C16.4911 17.5326 16.6667 17.1087 16.6667 16.6667V6.66669L11.6667 1.66669Z" stroke="#616161" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M11.6667 1.66669V6.66669H16.6667" stroke="#616161" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <label for="file-upload" class="file-label">파일 선택하기</label>
              <input
                id="file-upload"
                type="file"
                @change="handleFileChange"
                class="file-input-hidden"
              />
              <span v-if="formData.fileName" class="file-name">{{ formData.fileName }}</span>
            </div>
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
import { createOrUpdatePost } from '@/api.js'

export default {
  name: 'EventCreate',
  data() {
    return {
      formData: {
        title: '',
        content: '',
        file: null,
        fileName: '',
        author: '', // Will be set from user session or default
        year: new Date().getFullYear(),
        semester: '1'
      },
      loading: false,
      error: null
    }
  },
  methods: {
    handleFileChange(event) {
      const file = event.target.files[0]
      if (file) {
        this.formData.file = file
        this.formData.fileName = file.name
      }
    },
    handleCancel() {
      // Preserve category state when going back
      this.$router.push({ path: '/board', query: { category: 'events' } })
    },
    async handleSubmit() {
      this.loading = true
      this.error = null

      try {
        // Prepare post data according to API spec
        const postData = {
          author: this.formData.author || 'Anonymous', // TODO: Get from user session
          title: this.formData.title,
          content: this.formData.content,
          category: 'EVENT_INFO',
          year: this.formData.year,
          semester: this.formData.semester,
          is_internal: true
        }

        // Add event_info if needed (optional field)
        // postData.event_info = '';

        const response = await createOrUpdatePost(postData)
        console.log('Post created:', response.data)

        alert('행사정보가 저장되었습니다.')
        this.$router.push({ path: '/board', query: { category: 'events' } })
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

.event-create-page {
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

.file-input-wrapper {
  display: flex;
  align-items: center;
  height: 40px;
  background: #FCFCFC;
  padding: 9px 16px;
  box-sizing: border-box;
}

.file-input-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.file-label {
  font-weight: 500;
  font-size: 16px;
  line-height: 19px;
  color: #616161;
  cursor: pointer;
}

.file-label:hover {
  color: #910024;
}

.file-input-hidden {
  display: none;
}

.file-name {
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  color: #262626;
  margin-left: 8px;
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
