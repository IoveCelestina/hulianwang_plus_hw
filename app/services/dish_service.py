from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.dish import Dish, DishSpec

def compute_highlights(ai_metadata: dict) -> list[str]:
    meta = ai_metadata or {}
    taste = meta.get("taste", {}) if isinstance(meta.get("taste", {}), dict) else {}
    ingredients = meta.get("ingredients", []) if isinstance(meta.get("ingredients", []), list) else []
    temp = meta.get("temperature")

    highlights: list[str] = []

    spicy = taste.get("spicy")
    greasy = taste.get("greasy")
    light = taste.get("light")

    if isinstance(light, (int, float)) and light >= 3:
        highlights.append("清淡")
    elif isinstance(greasy, (int, float)) and greasy >= 4:
        highlights.append("重口")

    if isinstance(spicy, (int, float)):
        if spicy == 0:
            highlights.append("不辣")
        elif spicy >= 4:
            highlights.append("很辣")

    if temp == "hot":
        highlights.append("热菜")
    elif temp == "cold":
        highlights.append("冷菜")

    # 常见食材徽章（固定决策：仅展示少量）
    if any(x in ingredients for x in ["shrimp", "虾", "虾仁"]):
        highlights.append("含虾")
    if any(x in ingredients for x in ["beef", "牛肉"]):
        highlights.append("牛肉")
    if any(x in ingredients for x in ["chicken", "鸡肉"]):
        highlights.append("鸡肉")

    # diet / scenes
    diet = meta.get("diet", {}) if isinstance(meta.get("diet", {}), dict) else {}
    if diet.get("high_protein") is True:
        highlights.append("高蛋白")
    if diet.get("low_carb") is True:
        highlights.append("低碳水")

    # 去重并限制长度
    dedup = []
    for h in highlights:
        if h not in dedup:
            dedup.append(h)
    return dedup[:5]

async def list_dishes(
    db: AsyncSession,
    category_id: int | None,
    keyword: str | None,
    status: str = "on_sale",
) -> list[Dish]:
    stmt = select(Dish)
    if status:
        stmt = stmt.where(Dish.status == status)
    if category_id is not None:
        stmt = stmt.where(Dish.category_id == category_id)
    if keyword:
        # 固定决策：一期用 ILIKE，避免引入全文检索复杂度
        stmt = stmt.where(Dish.name.ilike(f"%{keyword}%"))
    res = await db.execute(stmt)
    return list(res.scalars().all())

async def get_dish_detail(db: AsyncSession, dish_id: int) -> tuple[Dish | None, list[DishSpec]]:
    dish_res = await db.execute(select(Dish).where(Dish.id == dish_id))
    dish = dish_res.scalar_one_or_none()
    if not dish:
        return None, []
    specs_res = await db.execute(select(DishSpec).where(DishSpec.dish_id == dish_id))
    specs = list(specs_res.scalars().all())
    return dish, specs

async def recommend_home(db: AsyncSession, user_tags: list[str]) -> list[Dish]:
    # 固定决策：首页推荐 = 在售菜里按（销量 + 评分）排序，再对“清淡/不辣/高蛋白”类标签微调
    res = await db.execute(select(Dish).where(Dish.status == "on_sale"))
    dishes = list(res.scalars().all())
    tags = set([t.lower() for t in (user_tags or [])])

    def score(d: Dish) -> float:
        s = float(d.sales_count) * 0.0003 + float(d.rating_avg) * 0.4
        meta = d.ai_metadata or {}
        taste = meta.get("taste", {}) if isinstance(meta.get("taste", {}), dict) else {}
        diet = meta.get("diet", {}) if isinstance(meta.get("diet", {}), dict) else {}
        spicy = taste.get("spicy", 2)
        light = taste.get("light", 2)

        if "light" in tags and isinstance(light, (int, float)) and light >= 3:
            s += 1.5
        if "no_spicy" in tags and isinstance(spicy, (int, float)) and spicy <= 1:
            s += 1.0
        if "high_protein" in tags and diet.get("high_protein") is True:
            s += 1.0
        return s

    ranked = sorted(dishes, key=score, reverse=True)
    return ranked[:20]

async def build_ai_candidates(
    db: AsyncSession,
    user_query: str,
    dietary_restrictions: list[str],
    limit: int = 30
) -> list[dict]:
    # 固定决策：候选集召回（一期）
    # 1) 只取在售
    # 2) 先按关键词命中 + 销量评分排序取 top
    # 3) 再做忌口/过敏源过滤（Python 过滤，保证正确）
    res = await db.execute(select(Dish).where(Dish.status == "on_sale"))
    dishes = list(res.scalars().all())
    q = (user_query or "").lower()
    restrictions = set([x.lower() for x in (dietary_restrictions or [])])

    def violates(d: Dish) -> bool:
        meta = d.ai_metadata or {}
        ing = meta.get("ingredients", [])
        allergens = meta.get("allergens", [])
        # 固定决策：restrictions 同时匹配 ingredients/allergens 任意即排除
        words = set([str(x).lower() for x in (ing or [])] + [str(x).lower() for x in (allergens or [])])
        return any(r in words for r in restrictions)

    def score(d: Dish) -> float:
        s = float(d.rating_avg) * 0.3 + float(d.sales_count) * 0.0004
        name = (d.name or "").lower()
        meta = d.ai_metadata or {}
        ing = " ".join([str(x).lower() for x in (meta.get("ingredients") or [])])
        if q:
            if q in name:
                s += 3.0
            if q in ing:
                s += 2.0
            if ("虾" in q or "shrimp" in q) and ("虾" in name or "shrimp" in ing):
                s += 3.0
            if ("清淡" in q or "light" in q):
                taste = meta.get("taste", {}) if isinstance(meta.get("taste", {}), dict) else {}
                if taste.get("light", 0) >= 3 or taste.get("spicy", 99) <= 1:
                    s += 2.0
        return s

    ranked = sorted([d for d in dishes if not violates(d)], key=score, reverse=True)[:limit]

    def compress(d: Dish) -> dict:
        meta = d.ai_metadata or {}
        taste = meta.get("taste", {}) if isinstance(meta.get("taste", {}), dict) else {}
        ingredients = meta.get("ingredients", []) if isinstance(meta.get("ingredients", []), list) else []
        return {
            "id": int(d.id),
            "name": d.name,
            "price": float(d.price),
            "meta": {
                "taste": {k: taste.get(k) for k in ["spicy","sweet","sour","numbing","greasy","light"]},
                "temperature": meta.get("temperature"),
                "ingredients": ingredients[:10],
                "allergens": (meta.get("allergens") or [])[:10],
                "diet": meta.get("diet", {}),
                "scenes": meta.get("scenes", []),
                "highlights": compute_highlights(meta),
                "rating": float(d.rating_avg),
                "sales": int(d.sales_count),
                "fallback_reason": ["在售", "口碑与热销靠前", "与你的表达更匹配"]
            }
        }

    return [compress(d) for d in ranked]
