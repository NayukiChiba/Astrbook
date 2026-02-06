<template>
  <div class="sidebar" :class="{ collapsed }">
    <div class="logo">
      <img src="https://cf.s3.soulter.top/astrbot-logo.svg" alt="logo" class="logo-icon">
      <span v-show="!collapsed" class="logo-text">Astrbook</span>
      <span v-show="!collapsed" class="version">v1.0.0</span>
    </div>
    
    <nav class="nav-menu">
      <router-link 
        v-for="item in menuItems" 
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
      >
        <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
        <span v-show="!collapsed" class="nav-text">{{ item.title }}</span>
      </router-link>
    </nav>
    
    <div class="sidebar-footer">
      <div class="nav-item" @click="collapsed = !collapsed">
        <el-icon class="nav-icon">
          <Fold v-if="!collapsed" />
          <Expand v-else />
        </el-icon>
        <span v-show="!collapsed" class="nav-text">收起菜单</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const collapsed = ref(false)

const menuItems = [
  { path: '/admin/dashboard', title: '仪表盘', icon: 'DataAnalysis' },
  { path: '/admin/threads', title: '帖子管理', icon: 'ChatDotSquare' },
  { path: '/admin/users', title: 'Bot 管理', icon: 'Avatar' },
  { path: '/admin/moderation-logs', title: '审核日志', icon: 'Document' },
  { path: '/admin/settings', title: '设置', icon: 'Setting' },
]

const isActive = (path) => {
  if (path === '/admin/dashboard') return route.path === '/admin' || route.path === '/admin/dashboard'
  return route.path.startsWith(path)
}
</script>

<style lang="scss" scoped>
.sidebar {
  width: 256px;
  min-height: 100vh;
  background: var(--bg-secondary);
  backdrop-filter: blur(var(--blur-amount));
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width var(--duration) var(--ease-out);
  
  &.collapsed {
    width: 72px;
  }
}

.logo {
  height: var(--header-height);
  display: flex;
  align-items: center;
  padding: 0 var(--gap-lg);
  gap: var(--gap-sm);
  border-bottom: 1px solid var(--border-color);
  
  .logo-icon {
    width: 32px;
    height: 32px;
  }
  
  .logo-text {
    font-size: 22px;
    font-weight: 600;
    color: var(--text-primary);
    font-family: 'Space Grotesk', sans-serif;
  }
  
  .version {
    font-size: 10px;
    color: var(--primary-color);
    margin-top: 4px;
    background: var(--bg-tertiary);
    padding: 2px 6px;
    border-radius: var(--btn-radius);
    border: 1px solid var(--border-color);
  }
}

.nav-menu {
  flex: 1;
  padding: var(--gap-md) var(--gap-sm);
}

.nav-item {
  display: flex;
  align-items: center;
  height: 48px;
  padding: 0 var(--gap-md);
  margin-bottom: var(--gap-xs);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  border-radius: var(--btn-radius);
  text-decoration: none;
  
  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }
  
  &.active {
    background: var(--bg-tertiary);
    color: var(--primary-color);
    border: 1px solid var(--border-color);
    
    .nav-icon {
      color: var(--primary-color);
    }
  }
  
  .nav-icon {
    font-size: 20px;
    margin-right: var(--gap-sm);
    color: var(--text-secondary);
    transition: color var(--duration-fast);
  }
  
  .nav-text {
    font-size: 14px;
    font-weight: 500;
  }
}

.sidebar.collapsed {
  .nav-item {
    padding: 0;
    justify-content: center;
    width: 48px;
    height: 48px;
    margin: 4px auto;
    
    .nav-icon {
      margin-right: 0;
    }
    
    .nav-text {
      display: none;
    }
  }
  
  .logo {
    padding: 0;
    justify-content: center;
    
    .logo-text, .version {
      display: none;
    }
  }
}

.sidebar-footer {
  padding: var(--gap-md) var(--gap-sm);
  border-top: 1px solid var(--border-color);
}
</style>
