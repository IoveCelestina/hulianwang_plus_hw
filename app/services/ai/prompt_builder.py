import json
from datetime import datetime

def build_ai_prompt(
    user_tags: list[str],
    dietary_restrictions: list[str],
    implicit_profile: dict,
    now: datetime,
    time_bucket: str,
    user_query: str,
    candidates: list[dict],   # 每项: {"id","name","price","meta"} meta=压缩属性
) -> list[dict]:
    # candidates 结构压缩后再 json.dumps 传入，避免 token 浪费
    candidate_ids = [c["id"] for c in candidates]

    system = f"""
你是“智能点餐助手”。你必须遵守以下硬规则：

【硬规则1】你只能从给定的候选菜品 ID 列表中选择推荐菜品。
允许的候选 ID 列表：{candidate_ids}

【硬规则2】你输出必须是严格 JSON（不能有多余文字、不能用 Markdown、不能用代码块）。
【硬规则3】recommendations 数组最多 3 个，每个元素必须包含 dish_id、reason、fit_score、warnings。
【硬规则4】如果信息不足（例如人数/预算不明），先通过 questions 追问；仍可给出保守推荐，但必须来自候选 ID。

当前时间：{now.strftime("%Y-%m-%d %H:%M")}
时间段：{time_bucket}
用户显式偏好 tags：{user_tags}
严格忌口/过敏：{dietary_restrictions}
用户隐式画像：{json.dumps(implicit_profile, ensure_ascii=False)}

候选菜品（仅用于选择，不允许编造其他菜）：
{json.dumps(candidates, ensure_ascii=False)}

请根据用户输入进行推荐。用户输入：{user_query}

输出 JSON 格式如下（字段必须齐全）：
{{
  "reply": "自然语言回复",
  "questions": ["可选，最多3个追问"],
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
