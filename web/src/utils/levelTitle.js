/**
 * 等级称号配置
 * 后端只返回 level 数值，前端根据等级渲染称号和样式
 */

const LEVEL_TITLES = {
  1:  { title: "0.5B",  color: "#9e9e9e", textColor: "#ffffff" },
  4:  { title: "7B",    color: "#43a047", textColor: "#ffffff" },
  8:  { title: "8B",    color: "#26a69a", textColor: "#ffffff" },
  10: { title: "14B",   color: "#29b6f6", textColor: "#ffffff" },
  12: { title: "32B",   color: "#5c6bc0", textColor: "#ffffff" },
  14: { title: "70B",   color: "#ab47bc", textColor: "#ffffff" },
  16: { title: "671B",  color: "#ff7043", textColor: "#ffffff" },
  18: { title: "MoE",   color: "linear-gradient(90deg, #f44336, #ff9800, #ffeb3b, #4caf50, #2196f3, #9c27b0)", textColor: "#ffffff", isGradient: true },
};

/**
 * 根据等级获取称号信息
 * @param {number} level - 用户等级
 * @returns {{ title: string, color: string, textColor: string, isGradient?: boolean }}
 */
export function getTitleForLevel(level) {
  const thresholds = [18, 16, 14, 12, 10, 8, 4, 1];
  for (const t of thresholds) {
    if (level >= t) return LEVEL_TITLES[t];
  }
  return LEVEL_TITLES[1];
}

/**
 * 获取等级对应的颜色
 * @param {number} level - 用户等级
 * @returns {string}
 */
export function getLevelColor(level) {
  return getTitleForLevel(level).color;
}

/**
 * 计算升级到下一级需要的经验
 * @param {number} level - 当前等级
 * @returns {number}
 */
export function expForLevel(level) {
  return Math.pow(level, 3);
}

/**
 * 计算当前等级的进度百分比
 * @param {number} exp - 当前经验
 * @param {number} level - 当前等级
 * @returns {number} 0-100
 */
export function getLevelProgress(exp, level) {
  const currentLevelExp = expForLevel(level);
  const nextLevelExp = expForLevel(level + 1);
  const progress = ((exp - currentLevelExp) / (nextLevelExp - currentLevelExp)) * 100;
  return Math.max(0, Math.min(100, progress));
}
