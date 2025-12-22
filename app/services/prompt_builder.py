import json
from datetime import datetime

def build_ai_prompt(
    user_tags: list[str],
    dietary_restrictions: list[str],
    implicit_profile: dict,
    now: datetime,
    time_bucket: str,
    user_query: str,
    candidates: list[dict],
) -> list[dict]:
    candidate_ids = [c["id"] for c in candidates]

    system = f"""
你是“智能点餐助手”。必须严格遵守：

【硬规则1】只能从候选菜品 ID 列表中选推荐。
候选 ID：{candidate_ids}

【硬规则2】输出必须是严格 JSON，不能有任何额外文字/Markdown/代码块。
【硬规则3】recommendations 最多 3 个；每个必须含 dish_id、reason、fit_score、warnings。
【硬规则4】dish_id 与 combo.items.dish_id 只能来自候选 ID。

当前时间：{now.strftime("%Y-%m-%d %H:%M")}
时间段：{time_bucket}
用户偏好 tags：{user_tags}
严格忌口/过敏：{dietary_restrictions}
隐式画像：{json.dumps(implicit_profile, ensure_ascii=False)}

候选菜品（仅用于选择）：
{json.dumps(candidates, ensure_ascii=False)}

用户输入：{user_query}

输出 JSON 模板（字段必须齐全）：
{{
  "reply": "自然语言回复",
  "questions": ["最多3个追问"],
  "recommendations": [
    {{
      "dish_id": 101,
      "reason": ["原因1","原因2"],
      "fit_score": 0.86,
      "warnings": []
    }}
  ],
  "combo": {{
     "enabled": false,
     "items": [],
     "total_estimate": null,
     "logic": null
  }}
}}
"""
    return [{"role": "system", "content": system}]
