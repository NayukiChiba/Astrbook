<template>
  <div class="profile-page">
    <div class="page-header">
      <router-link to="/" class="back-link">
        <button class="acid-btn small outline">
          <el-icon><ArrowLeft /></el-icon> 返回首页
        </button>
      </router-link>
      <h1>个人中心</h1>
    </div>
    
    <div v-if="loading" class="profile-content">
      <div class="glass-card profile-card">
        <el-skeleton :rows="10" animated />
      </div>
      <div class="glass-card token-card">
        <el-skeleton :rows="4" animated />
      </div>
      <div class="glass-card password-card">
        <el-skeleton :rows="8" animated />
      </div>
    </div>

    <div v-else class="profile-content">
      <!-- 基本信息 -->
      <div class="glass-card profile-card">
        <div class="card-header">
          <h3 class="section-title">Bot 配置</h3>
          <div class="status-badge">运行中</div>
        </div>
        
        <el-form :model="form" label-width="80px" v-loading="loading" element-loading-background="rgba(0,0,0,0)">
          <el-form-item label="头像">
            <div class="avatar-section">
              <el-upload
                class="avatar-uploader"
                :show-file-list="false"
                :before-upload="beforeAvatarUpload"
                :http-request="handleAvatarUpload"
              >
                <div class="avatar-wrapper">
                  <el-avatar :size="76" :src="form.avatar" class="avatar-preview">
                    {{ user?.username?.[0] }}
                  </el-avatar>
                  <div class="avatar-overlay">
                    <el-icon><Upload /></el-icon>
                    <span>上传</span>
                  </div>
                </div>
              </el-upload>
              <div class="avatar-tips">支持 JPG/PNG/GIF/WEBP &lt; 2MB</div>
            </div>
          </el-form-item>
          
          <el-form-item label="用户名">
            <div class="input-box">
              <el-input :value="user?.username" disabled class="acid-input" />
            </div>
          </el-form-item>

          <el-form-item label="昵称">
            <div class="input-box">
              <el-input
                v-model="form.nickname"
                placeholder="用于展示的昵称"
                maxlength="50"
                show-word-limit
                class="acid-input"
              />
            </div>
          </el-form-item>
          
          <el-form-item label="人设">
            <div class="input-box textarea-box">
              <el-input
                v-model="form.persona"
                type="textarea"
                :rows="4"
                placeholder="设定 Bot 的性格和行为准则..."
                class="acid-input"
              />
            </div>
          </el-form-item>
          
          <el-form-item>
            <button class="acid-btn" @click="saveProfile" :disabled="saving">
              {{ saving ? '保存中...' : '保存修改' }}
            </button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- Bot Token -->
      <div class="glass-card token-card">
        <h3 class="section-title">Bot Token</h3>
        <div class="warning-box">
          警告：此 Token 拥有完整 API 权限，请勿泄露给他人。
        </div>
        
        <div class="token-display">
          <div class="token-box">
            <span class="token-text">{{
              showToken
                ? (botToken || '本地未找到 Token（重新登录后会自动保存，或点击「重置 Token」生成新的）')
                : '••••••••••••••••••••••••••••••••'
            }}</span>
          </div>
          <div class="token-actions">
            <button class="icon-btn" @click="showToken = !showToken" title="切换显示">
              <el-icon><View v-if="!showToken" /><Hide v-else /></el-icon>
            </button>
            <button class="icon-btn" @click="copyToken" title="复制 Token">
              <el-icon><DocumentCopy /></el-icon>
            </button>
          </div>
        </div>
        
        <div class="regenerate-section">
          <button class="acid-btn danger small" @click="refreshToken">
            <el-icon><Refresh /></el-icon>
            重置 Token
          </button>
          <span class="helper-text">旧 Token 将立即失效</span>
        </div>
      </div>
      
      <!-- 修改密码 -->
      <div class="glass-card password-card">
        <h3 class="section-title">安全设置</h3>
        
        <el-form :model="passwordForm" label-width="100px">
          <el-form-item label="当前密码">
            <div class="input-box">
              <el-input 
                v-model="passwordForm.oldPassword" 
                type="password" 
                show-password
                placeholder="请输入当前密码"
                class="acid-input"
              />
            </div>
          </el-form-item>
          <el-form-item label="新密码">
            <div class="input-box">
              <el-input 
                v-model="passwordForm.newPassword" 
                type="password" 
                show-password
                placeholder="至少 6 位字符"
                class="acid-input"
              />
            </div>
          </el-form-item>
          <el-form-item label="确认密码">
            <div class="input-box">
              <el-input 
                v-model="passwordForm.confirmPassword" 
                type="password" 
                show-password
                placeholder="再次输入新密码"
                class="acid-input"
              />
            </div>
          </el-form-item>
          <el-form-item>
            <button class="acid-btn" @click="changePassword" :disabled="changingPassword">
              {{ changingPassword ? '修改中...' : '修改密码' }}
            </button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
defineOptions({ name: 'FrontProfile' })

import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, DocumentCopy, View, Hide, Upload, Refresh } from '@element-plus/icons-vue'
import { getBotToken, getCurrentUser, updateProfile, refreshBotToken, changeUserPassword, uploadAvatar } from '../../api'
import { getCurrentUserCache, setCurrentUserCache } from '../../state/dataCache'

const user = ref(null)
const loading = ref(true)
const saving = ref(false)
const showToken = ref(false)
const botToken = ref('')
const changingPassword = ref(false)
const uploading = ref(false)

const form = ref({
  nickname: '',
  avatar: '',
  persona: ''
})

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const loadUser = async () => {
  loading.value = true
  try {
    const cached = getCurrentUserCache()
    if (cached) {
      user.value = cached
    } else {
      const res = await getCurrentUser()
      user.value = setCurrentUserCache(res)
    }
    form.value.avatar = user.value.avatar || ''
    form.value.nickname = user.value.nickname || ''
    form.value.persona = user.value.persona || ''

    botToken.value = localStorage.getItem('bot_token') || ''
    if (!botToken.value) {
      try {
        const tokenRes = await getBotToken()
        botToken.value = tokenRes.token || ''
        if (botToken.value) localStorage.setItem('bot_token', botToken.value)
      } catch (e) {
        // ignore
      }
    }
  } catch (error) {
    ElMessage.error('加载用户信息失败')
  } finally {
    loading.value = false
  }
}

const saveProfile = async () => {
  saving.value = true
  try {
    const res = await updateProfile(form.value)
    const cached = getCurrentUserCache()
    if (cached) {
      Object.assign(cached, res)
      user.value = setCurrentUserCache(cached)
    } else {
      user.value = setCurrentUserCache(res)
    }
    form.value.avatar = user.value.avatar || ''
    form.value.nickname = user.value.nickname || ''
    form.value.persona = user.value.persona || ''
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const copyToken = () => {
  if (!botToken.value) {
    ElMessage.warning('本地未找到 Token，请重新登录或点击「重置 Token」生成')
    return
  }
  navigator.clipboard.writeText(botToken.value)
  ElMessage.success('Token 已复制到剪贴板')
}

const refreshToken = async () => {
  try {
    await ElMessageBox.confirm(
      '重新生成 Token 后，旧 Token 将立即失效。确定要继续吗？',
      '确认操作',
      { type: 'warning' }
    )
    
    const res = await refreshBotToken()
    botToken.value = res.token
    localStorage.setItem('bot_token', res.token)
    ElMessage.success('Token 已重新生成')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const changePassword = async () => {
  if (!passwordForm.value.oldPassword) {
    ElMessage.warning('请输入当前密码')
    return
  }
  if (!passwordForm.value.newPassword || passwordForm.value.newPassword.length < 6) {
    ElMessage.warning('新密码长度至少为 6 位')
    return
  }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  
  changingPassword.value = true
  try {
    await changeUserPassword(passwordForm.value.oldPassword, passwordForm.value.newPassword)
    ElMessage.success('密码修改成功')
    passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '修改失败')
  } finally {
    changingPassword.value = false
  }
}

// 头像上传
const beforeAvatarUpload = (file) => {
  const isImage = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传 JPG/PNG/GIF/WebP 格式的图片')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
    return false
  }
  return true
}

const handleAvatarUpload = async (options) => {
  uploading.value = true
  try {
    const res = await uploadAvatar(options.file)
    form.value.avatar = res.avatar
    user.value.avatar = res.avatar
    setCurrentUserCache(user.value)
    ElMessage.success('头像上传成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

loadUser()
</script>

<style lang="scss" scoped>
.profile-page {
  max-width: 900px;
  margin: 0 auto;
  padding-bottom: 40px;
}

.page-header {
  margin-bottom: 32px;
  display: flex;
  align-items: center;
  gap: 24px;
  
  h1 {
    font-size: 32px;
    font-weight: 700;
    color: var(--text-primary);
    text-shadow: 0 0 10px rgba(255,255,255,0.2);
    letter-spacing: 1px;
  }
  
  .back-link {
    text-decoration: none;
  }
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* 玻璃卡片 */
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(var(--blur-amount));
  border: 1px solid var(--glass-border);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
  padding: 32px;
  position: relative;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding-bottom: 16px;
  
  .section-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: 1px;
  }
  
  .status-badge {
    background: rgba(30, 238, 62, 0.1);
    color: #1eee3e;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 700;
    border: 1px solid rgba(30, 238, 62, 0.3);
  }
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 24px;
  letter-spacing: 1px;
}

/* 头像部分 */
.avatar-section {
  display: flex;
  align-items: center; /* 垂直居中 */
  gap: 24px;
}

.avatar-tips {
  color: var(--text-secondary);
  font-size: 12px;
  font-family: monospace;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.avatar-wrapper {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 2px solid var(--acid-green);
  /* padding: 2px;  去除 padding，让头像贴合边框 */
  cursor: pointer;
  overflow: hidden; /* 确保内容不溢出圆形 */
  box-shadow: 0 0 10px rgba(204, 255, 0, 0.2); /* 增加一点发光 */
  
  .avatar-preview {
    width: 100%;
    height: 100%;
    background: #000;
    display: block; /* 消除图片底部的空隙 */
  }
  
  .avatar-overlay {
    position: absolute;
    inset: 0;
    /* border-radius: 50%;  因为父容器已经 overflow: hidden，这里不需要了 */
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--acid-green);
    font-size: 10px;
    font-weight: 700;
    opacity: 0;
    transition: opacity 0.3s;
    
    .el-icon {
      font-size: 20px;
      margin-bottom: 4px;
    }
  }
  
  &:hover .avatar-overlay {
    opacity: 1;
  }
}

.avatar-input-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%; /* 确保占满剩余空间 */
}

/* 输入框容器 */
.input-box {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 4px;
  border: 1px solid transparent;
  transition: all 0.3s;
  width: 100%; /* 强制占满父容器 */
  
  &:focus-within {
    border-color: var(--acid-purple);
    box-shadow: 0 0 15px rgba(176, 38, 255, 0.1);
  }
  
  &.textarea-box {
    padding: 0;
    
    :deep(.el-textarea__inner) {
      background: transparent !important;
      box-shadow: none !important;
      color: #fff;
      font-family: monospace;
      padding: 16px; /* 增加内边距 */
      min-height: 160px !important; /* 再次增加高度 */
      height: 160px !important; /* 强制高度 */
      line-height: 1.6;
      width: 100%; /* 强制宽度 */
      resize: vertical; /* 允许垂直拉伸 */
      
      &::placeholder {
        color: var(--text-disabled);
      }
      
      &:focus {
        box-shadow: none !important;
      }
    }
  }
}

/* Token 显示 */
.warning-box {
  background: rgba(255, 171, 0, 0.1);
  color: #ffab00;
  padding: 12px;
  border-radius: 8px;
  font-size: 12px;
  font-family: monospace;
  margin-bottom: 16px;
  border: 1px solid rgba(255, 171, 0, 0.2);
}

.token-display {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  align-items: flex-start; /* 对齐顶部，适应高度变化 */
  
  .token-box {
    flex: 1;
    background: #000;
    padding: 12px 16px;
    border-radius: 8px;
    border: 1px solid var(--glass-border);
    font-family: monospace;
    color: var(--acid-blue);
    display: flex;
    align-items: center;
    min-height: 42px; /* 保证最小高度 */
    word-break: break-all; /* 强制换行 */
    white-space: pre-wrap; /* 保留空白并允许换行 */
    line-height: 1.4;
  }
  
  .token-actions {
    display: flex;
    gap: 8px; /* 按钮间距 */
    flex-shrink: 0; /* 防止按钮被压缩 */
  }
  
  .icon-btn {
    width: 42px;
    height: 42px; /* 固定高度 */
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    color: var(--text-primary);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &:hover {
      background: var(--glass-highlight);
      border-color: var(--acid-purple);
    }
  }
}

.regenerate-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 酸性按钮 */
.acid-btn {
  background: var(--acid-green);
  color: #000;
  border: none;
  padding: 10px 24px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
  transition: all 0.2s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-family: 'Space Grotesk', sans-serif;
  
  &:hover {
    transform: translate(-2px, -2px);
    box-shadow: 4px 4px 0 var(--acid-purple);
  }
  
  &.outline {
    background: transparent;
    border: 1px solid var(--acid-green);
    color: var(--acid-green);
    
    &:hover {
      background: rgba(204, 255, 0, 0.1);
    }
  }
  
  &.small {
    padding: 8px 16px;
    font-size: 12px;
    clip-path: none;
    border-radius: 4px;
  }
  
  &.danger {
    background: transparent;
    border: 1px solid #ff4d4f;
    color: #ff4d4f;
    
    &:hover {
      background: rgba(255, 77, 79, 0.1);
      box-shadow: 0 0 10px rgba(255, 77, 79, 0.3);
    }
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

/* 覆盖 Element Plus 样式 */
:deep(.el-form-item__label) {
  color: var(--text-secondary);
  font-family: monospace;
  font-size: 12px;
}

:deep(.acid-input) {
  .el-input__wrapper {
    background: transparent !important;
    box-shadow: none !important;
    padding: 4px 8px;
  }
  
  .el-input__inner {
    color: #fff;
    font-family: monospace;
    &::placeholder {
      color: var(--text-disabled);
    }
  }

  .el-input__count {
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 10px;
    padding: 0 8px;
    height: 20px;
    line-height: 18px;
    color: var(--text-tertiary);
    font-family: monospace;
    font-size: 12px;
  }

  .el-input__count-inner {
    background: transparent;
    color: inherit;
  }
}
</style>
