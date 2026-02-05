"""
内容审核模块 - 使用 OpenAI 兼容接口进行内容安全审核
"""
import httpx
import json
import logging
from typing import Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
from .models import SystemSettings, ModerationLog

logger = logging.getLogger(__name__)

# 默认审核 Prompt
DEFAULT_MODERATION_PROMPT = """你是内容安全审核员。请判断以下内容是否存在严重违规。

审核原则：宽松审核，仅拦截直白露骨的违规内容。
- 允许：正常讨论、玩笑调侃、轻微擦边、二次元内容、情感表达
- 允许：历史讨论、时事评论、观点表达（非极端）
- 允许：虚构创作、角色扮演、艺术表达

仅在以下情况拒绝：
1. 色情内容（sexual）：直白露骨的性行为描写、真人色情内容
2. 暴力内容（violence）：具体详细的伤害教程、真实暴力威胁
3. 极端内容（extreme）：煽动仇恨、恐怖主义、严重违法信息

如有疑虑，倾向于通过。

请以 JSON 格式回复，不要包含其他内容：
{"passed": true, "category": "none", "reason": ""}
或
{"passed": false, "category": "sexual/violence/extreme", "reason": "简短说明"}

待审核内容：
{content}"""


@dataclass
class ModerationResult:
    """审核结果"""
    passed: bool
    category: str = "none"  # none / sexual / violence / political
    reason: str = ""
    error: Optional[str] = None


class ContentModerator:
    """内容审核器"""
    
    def __init__(self, db: Session):
        self.db = db
        self._load_settings()
    
    def _load_settings(self):
        """从数据库加载配置"""
        self.enabled = self._get_setting("moderation_enabled", "false") == "true"
        self.api_base = self._get_setting("moderation_api_base", "https://api.openai.com/v1")
        self.api_key = self._get_setting("moderation_api_key", "")
        self.model = self._get_setting("moderation_model", "gpt-4o-mini")
        self.prompt = self._get_setting("moderation_prompt", DEFAULT_MODERATION_PROMPT)
    
    def _get_setting(self, key: str, default: str = "") -> str:
        """获取设置值"""
        setting = self.db.query(SystemSettings).filter(SystemSettings.key == key).first()
        return setting.value if setting and setting.value else default
    
    async def check(
        self,
        content: str,
        content_type: str,
        user_id: int,
        content_id: Optional[int] = None
    ) -> ModerationResult:
        """
        审核内容
        
        Args:
            content: 待审核内容
            content_type: 内容类型 (thread / reply / sub_reply)
            user_id: 发布者 ID
            content_id: 内容 ID（可选，审核通过后会有）
        
        Returns:
            ModerationResult: 审核结果
        """
        # 如果未启用审核，直接通过
        if not self.enabled:
            return ModerationResult(passed=True)
        
        # 检查配置是否完整
        if not self.api_key or not self.api_base or not self.model:
            logger.warning("审核配置不完整，跳过审核")
            return ModerationResult(passed=True)
        
        try:
            result = await self._call_llm(content)
            
            # 记录审核日志
            self._log_moderation(
                content_type=content_type,
                content_id=content_id,
                user_id=user_id,
                content_preview=content[:500] if content else "",
                passed=result.passed,
                flagged_category=result.category if not result.passed else None,
                reason=result.reason if not result.passed else None,
                model_used=self.model
            )
            
            return result
            
        except Exception as e:
            logger.error(f"审核请求失败: {e}")
            # 审核失败时默认通过（可配置）
            return ModerationResult(passed=True, error=str(e))
    
    async def _call_llm(self, content: str) -> ModerationResult:
        """调用 LLM 进行审核"""
        # 构建完整的 prompt
        full_prompt = self.prompt.replace("{content}", content)
        
        url = f"{self.api_base.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": full_prompt}
            ],
            "temperature": 0,
            "max_tokens": 200
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        
        # 解析响应
        reply = data["choices"][0]["message"]["content"].strip()
        
        # 尝试解析 JSON
        try:
            # 处理可能的 markdown 代码块
            if reply.startswith("```"):
                reply = reply.split("```")[1]
                if reply.startswith("json"):
                    reply = reply[4:]
                reply = reply.strip()
            
            result = json.loads(reply)
            return ModerationResult(
                passed=result.get("passed", True),
                category=result.get("category", "none"),
                reason=result.get("reason", "")
            )
        except json.JSONDecodeError:
            logger.warning(f"无法解析审核响应: {reply}")
            # 无法解析时默认通过
            return ModerationResult(passed=True)
    
    def _log_moderation(
        self,
        content_type: str,
        content_id: Optional[int],
        user_id: int,
        content_preview: str,
        passed: bool,
        flagged_category: Optional[str],
        reason: Optional[str],
        model_used: str
    ):
        """记录审核日志"""
        log = ModerationLog(
            content_type=content_type,
            content_id=content_id,
            user_id=user_id,
            content_preview=content_preview,
            passed=passed,
            flagged_category=flagged_category,
            reason=reason,
            model_used=model_used
        )
        self.db.add(log)
        # 注意：不在这里 commit，由调用方统一处理


async def fetch_available_models(api_base: str, api_key: str) -> list[str]:
    """从 API 获取可用模型列表"""
    url = f"{api_base.rstrip('/')}/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    
    # 提取模型 ID 列表
    models = []
    for model in data.get("data", []):
        model_id = model.get("id", "")
        if model_id:
            models.append(model_id)
    
    # 按名称排序
    models.sort()
    return models


def get_moderator(db: Session) -> ContentModerator:
    """获取审核器实例"""
    return ContentModerator(db)
