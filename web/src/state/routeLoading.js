import { ref } from 'vue'

export const isRouteLoading = ref(false)

let pending = 0
let timer = null

const SHOW_DELAY_MS = 150

export const startRouteLoading = () => {
  pending += 1
  if (timer) return
  timer = setTimeout(() => {
    timer = null
    if (pending > 0) isRouteLoading.value = true
  }, SHOW_DELAY_MS)
}

export const stopRouteLoading = () => {
  pending = Math.max(0, pending - 1)
  if (pending !== 0) return

  if (timer) {
    clearTimeout(timer)
    timer = null
  }
  isRouteLoading.value = false
}

