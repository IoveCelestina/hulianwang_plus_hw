import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.core.deps import require_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.models.user_preferences import UserPreferences
from app.services.ai.recommender import AiRecommender
from app.services.dish_service import build_ai_candidates
from app.schemas.chat import AiResponse

router = APIRouter(prefix="/ai")
recommender = AiRecommender()

@router.post("/sessions")
async def create_session(user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    s = ChatSession(user_id=int(user.id), summary=None)
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return {"session_id": int(s.id)}

@router.post("/sessions/{session_id}/messages", response_model=AiResponse)
async def send_message(session_id: int, payload: dict, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    content = str(payload.get("content") or "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="empty_content")

    # session 校验
    sres = await db.execute(select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == int(user.id)))
    if not sres.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="session_not_found")

    # preferences
    pres = await db.execute(select(UserPreferences).where(UserPreferences.user_id == int(user.id)))
    pref = pres.scalar_one_or_none()
    if not pref:
        pref = UserPreferences(user_id=int(user.id), explicit_tags=[], implicit_profile={}, dietary_restrictions=[])
        db.add(pref)
        await db.commit()
        await db.refresh(pref)

    # 写 user message
    db.add(ChatMessage(session_id=session_id, role="user", content=content))
    await db.commit()

    # 候选集（在售 + 关键词/热销/评分 + 忌口过滤）
    candidates = await build_ai_candidates(db, content, list(pref.dietary_restrictions or []), limit=30)

    # 推荐（严格候选）
    ai_resp, meta = await recommender.recommend(
        user_tags=list(pref.explicit_tags or []),
        dietary_restrictions=list(pref.dietary_restrictions or []),
        implicit_profile=dict(pref.implicit_profile or {}),
        user_query=content,
        candidates=candidates
    )

    # 写 assistant message（可追溯：candidate ids + recommended ids）
    db.add(ChatMessage(
        session_id=session_id,
        role="assistant",
        content=ai_resp.reply,
        recommended_dish_ids=[r.dish_id for r in ai_resp.recommendations],
        candidate_dish_ids=[c["id"] for c in candidates],
        meta=meta
    ))
    await db.commit()

    return ai_resp

@router.post("/sessions/{session_id}/messages:stream")
async def send_message_stream(session_id: int, payload: dict, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    content = str(payload.get("content") or "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="empty_content")

    sres = await db.execute(select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == int(user.id)))
    if not sres.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="session_not_found")

    pres = await db.execute(select(UserPreferences).where(UserPreferences.user_id == int(user.id)))
    pref = pres.scalar_one_or_none()
    if not pref:
        pref = UserPreferences(user_id=int(user.id), explicit_tags=[], implicit_profile={}, dietary_restrictions=[])
        db.add(pref)
        await db.commit()
        await db.refresh(pref)

    db.add(ChatMessage(session_id=session_id, role="user", content=content))
    await db.commit()

    candidates = await build_ai_candidates(db, content, list(pref.dietary_restrictions or []), limit=30)
    ai_resp, meta = await recommender.recommend(
        user_tags=list(pref.explicit_tags or []),
        dietary_restrictions=list(pref.dietary_restrictions or []),
        implicit_profile=dict(pref.implicit_profile or {}),
        user_query=content,
        candidates=candidates
    )

    db.add(ChatMessage(
        session_id=session_id,
        role="assistant",
        content=ai_resp.reply,
        recommended_dish_ids=[r.dish_id for r in ai_resp.recommendations],
        candidate_dish_ids=[c["id"] for c in candidates],
        meta=meta
    ))
    await db.commit()

    async def gen():
        # token（分段模拟流，接口稳定；你二期可替换为模型真流）
        text = ai_resp.reply
        for i in range(0, len(text), 24):
            part = text[i:i+24]
            yield f"event: token\ndata: {json.dumps(part, ensure_ascii=False)}\n\n"

        yield f"event: recommendations\ndata: {ai_resp.model_dump_json()}\n\n"
        yield f"event: done\ndata: {ai_resp.model_dump_json()}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
