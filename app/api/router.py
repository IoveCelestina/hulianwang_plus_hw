from fastapi import APIRouter
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.addresses import router as addr_router
from app.api.routes.dishes import router as dishes_router
from app.api.routes.cart import router as cart_router
from app.api.routes.orders import router as orders_router
from app.api.routes.reviews import router as reviews_router
from app.api.routes.chat_ai import router as chat_router

from app.api.routes.admin import router as admin_router

api_router = APIRouter()
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(users_router, tags=["users"])
api_router.include_router(addr_router, tags=["addresses"])
api_router.include_router(dishes_router, tags=["dishes"])
api_router.include_router(cart_router, tags=["cart"])
api_router.include_router(orders_router, tags=["orders"])
api_router.include_router(reviews_router, tags=["reviews"])
api_router.include_router(chat_router, tags=["ai"])
api_router.include_router(admin_router, tags=["admin"])
