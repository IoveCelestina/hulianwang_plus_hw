from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.db.session import get_db
from app.core.deps import require_user
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.models.events import PreferenceEvent
from app.schemas.auth import MeOut
from app.schemas.user import PreferencesOut, PreferencesUpdateIn

router = APIRouter(prefix="/users")

@router.get("/me", response_model=MeOut)
async def me(user: User = Depends(require_user)):
    return MeOut(
        id=int(user.id),
        username=user.username,
        role=user.role,
        created_at=str(user.created_at) if user.created_at else None
    )

@router.get("/preferences", response_model=PreferencesOut)
async def get_preferences(user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(UserPreferences).where(UserPreferences.user_id == int(user.id)))
    pref = res.scalar_one_or_none()
    if not pref:
        pref = UserPreferences(user_id=int(user.id), explicit_tags=[], implicit_profile={}, dietary_restrictions=[])
        db.add(pref)
        await db.commit()
        await db.refresh(pref)
    return PreferencesOut(
        explicit_tags=list(pref.explicit_tags or []),
        implicit_profile=dict(pref.implicit_profile or {}),
        dietary_restrictions=list(pref.dietary_restrictions or [])
    )

@router.put("/preferences", response_model=PreferencesOut)
async def update_preferences(
    data: PreferencesUpdateIn,
    user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(UserPreferences).where(UserPreferences.user_id == int(user.id)))
    pref = res.scalar_one_or_none()
    created = False
    if not pref:
        pref = UserPreferences(user_id=int(user.id), explicit_tags=[], implicit_profile={}, dietary_restrictions=[])
        db.add(pref)
        created = True

    if data.explicit_tags is not None:
        pref.explicit_tags = data.explicit_tags
    if data.dietary_restrictions is not None:
        pref.dietary_restrictions = data.dietary_restrictions

    pref.last_updated = datetime.utcnow()
    db.add(pref)

    db.add(PreferenceEvent(
        user_id=int(user.id),
        event_type="tag_init" if created else "manual_edit",
        payload={"explicit_tags": pref.explicit_tags, "dietary_restrictions": pref.dietary_restrictions}
    ))

    await db.commit()
    await db.refresh(pref)

    return PreferencesOut(
        explicit_tags=list(pref.explicit_tags or []),
        implicit_profile=dict(pref.implicit_profile or {}),
        dietary_restrictions=list(pref.dietary_restrictions or [])
    )
