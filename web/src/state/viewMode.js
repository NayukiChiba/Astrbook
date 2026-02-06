/**
 * 视图模式管理
 * 用于在首页切换紧凑/舒适视图
 */

import { ref } from 'vue'

// 视图模式：compact | comfortable
const viewMode = ref(localStorage.getItem('viewMode') || 'comfortable')

export function useViewMode() {
  const setViewMode = (mode) => {
    viewMode.value = mode
    localStorage.setItem('viewMode', mode)
  }

  const toggleViewMode = (mode) => {
    if (mode) {
      setViewMode(mode)
    } else {
      // 切换模式
      setViewMode(viewMode.value === 'compact' ? 'comfortable' : 'compact')
    }
  }

  return {
    viewMode,
    setViewMode,
    toggleViewMode
  }
}
