import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getCurrentTheme, setTheme, isDarkTheme } from '../utils/theme'

const isBrowser = typeof window !== 'undefined'

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref(isBrowser ? getCurrentTheme() : 'dark')
  const isDark = ref(isBrowser ? isDarkTheme() : true)

  const toggleTheme = () => {
    const next = isDark.value ? 'light' : 'dark'
    currentTheme.value = next
    if (isBrowser) setTheme(next)
    isDark.value = !isDark.value
  }

  const setCurrentTheme = (themeKey) => {
    currentTheme.value = themeKey
    if (isBrowser) setTheme(themeKey)
    isDark.value = isBrowser ? isDarkTheme() : (themeKey !== 'light')
  }

  return {
    currentTheme,
    isDark,
    toggleTheme,
    setCurrentTheme
  }
})
