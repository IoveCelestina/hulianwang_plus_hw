import time
from datetime import datetime
from app.services.ai.deepseek_client import DeepSeekClient
from app.services.ai.prompt_builder import build_ai_prompt
from app.services.ai.validators import parse_and_validate_ai_json, enforce_candidate_only, AiValidationError
from app.schemas.chat import AiResponse, AiRecommendation, AiCombo

def get_time_bucket(now: datetime) -> str:
    h = now.hour
    if 5 <= h < 11:
        return "breakfast"
    if 11 <= h < 15:
        return "lunch"
    if 15 <= h < 22:
        return "dinner"
    return "late_night"

def heuristic_fallback(user_tags: list[str], user_query: str, candidates: list[dict]) -> AiResponse:
    q = (user_query or "").lower()
    tags = set([t.lower() for t in (user_tags or [])])

    def score(c: dict) -> float:
        s = 0.0
        name = (c.get("name") or "").lower()
        meta = c.get("meta") or {}
        hl = " ".join(meta.get("highlights", [])).lower()
        ing = " ".join([str(x).lower() for x in (meta.get("ingredients") or [])])

        if "虾" in q or "shrimp" in q:
            if "虾" in name or "shrimp" in name or "虾" in ing or "shrimp" in ing:
                s += 3.0
        if "清淡" in q or "light" in q:
            if "清淡" in hl or "不辣" in hl:
                s += 2.0

        if "no_spicy" in tags and ("很辣" in hl or "辣" in hl):
            s -= 3.0
        if "light" in tags and ("清淡" in hl):
            s += 1.5

        s += float(meta.get("rating", 4.5)) * 0.2
        s += float(meta.get("sales", 0)) * 0.0002
        return s

    ranked = sorted(candidates, key=score, reverse=True)[:3]
    recs = []
    for i, c in enumerate(ranked):
        recs.append(AiRecommendation(
            dish_id=int(c["id"]),
            reason=c.get("meta", {}).get("fallback_reason", ["更符合你的需求与口碑热度"]),
            fit_score=max(0.55, 0.75 - i * 0.08),
            warnings=[]
        ))

    return AiResponse(
        reply="我已根据当前可售菜品与口碑热度为你筛选了更稳妥的选择（本次为规则推荐）。",
        questions=[],
        recommendations=recs,
        combo=AiCombo(enabled=False, items=[], total_estimate=None, logic=None)
    )

class AiRecommender:
    def __init__(self):
        self.client = DeepSeekClient()

    async def recommend(self, user_tags, dietary_restrictions, implicit_profile, user_query, candidates):
        now = datetime.now()
        bucket = get_time_bucket(now)
        candidate_ids = set([c["id"] for c in candidates])

        messages = build_ai_prompt(
            user_tags=user_tags,
            dietary_restrictions=dietary_restrictions,
            implicit_profile=implicit_profile,
            now=now,
            time_bucket=bucket,
            user_query=user_query,
            candidates=candidates,
        )

        t0 = time.time()
        try:
            raw = await self.client.chat_completion(messages)
            resp = parse_and_validate_ai_json(raw)
            resp = enforce_candidate_only(resp, candidate_ids)
            return resp, {"degraded": False, "latency_ms": int((time.time()-t0)*1000)}
        except AiValidationError:
            # 修复一次
            try:
                repair = messages + [{"role": "user", "content": "上一次输出不合规。请严格只输出 JSON，且所有 dish_id 必须来自候选 ID。重新输出。"}]
                raw2 = await self.client.chat_completion(repair)
                resp2 = parse_and_validate_ai_json(raw2)
                resp2 = enforce_candidate_only(resp2, candidate_ids)
                return resp2, {"degraded": False, "repaired": True, "latency_ms": int((time.time()-t0)*1000)}
            except Exception:
                # 最终降级：仍只从候选
                return heuristic_fallback(user_tags, user_query, candidates), {"degraded": True, "latency_ms": int((time.time()-t0)*1000)}
