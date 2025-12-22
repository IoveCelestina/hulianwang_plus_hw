-- =========================
-- AI 智能点餐系统 - 初始化SQL
-- PostgreSQL 13+
-- =========================

-- 可选：扩展
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- =========================
-- 1. 用户与权限
-- =========================
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) NOT NULL DEFAULT 'user', -- user/admin
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

-- =========================
-- 2. 用户画像（AI 大脑）
-- =========================
CREATE TABLE user_preferences (
    user_id BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    explicit_tags JSONB NOT NULL DEFAULT '[]',          -- ["light","no_spicy"]
    implicit_profile JSONB NOT NULL DEFAULT '{}',       -- {"avg_spend": 50}
    dietary_restrictions JSONB NOT NULL DEFAULT '[]',   -- ["cilantro","peanut"]
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_preferences_last_updated ON user_preferences (last_updated DESC);

-- =========================
-- 3. 用户地址
-- =========================
CREATE TABLE user_addresses (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address_line VARCHAR(255) NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_addresses_user ON user_addresses (user_id, created_at DESC);
CREATE INDEX idx_user_addresses_default ON user_addresses (user_id, is_default);

-- =========================
-- 4. 分类与菜品
-- =========================
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    sort_order INT DEFAULT 0
);

CREATE TABLE dishes (
    id BIGSERIAL PRIMARY KEY,
    category_id INT REFERENCES categories(id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'on_sale', -- on_sale/sold_out/offline
    ai_metadata JSONB NOT NULL DEFAULT '{}',       -- AI 决策元数据（结构化）
    sales_count INT NOT NULL DEFAULT 0,
    rating_avg DECIMAL(3,1) NOT NULL DEFAULT 5.0,
    rating_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI 检索索引
CREATE INDEX idx_dishes_ai_metadata_gin ON dishes USING GIN (ai_metadata);
CREATE INDEX idx_dishes_category_status ON dishes (category_id, status);
CREATE INDEX idx_dishes_sales_count ON dishes (sales_count DESC);
CREATE INDEX idx_dishes_rating ON dishes (rating_avg DESC);

-- =========================
-- 5. 菜品规格
-- =========================
CREATE TABLE dish_specs (
    id BIGSERIAL PRIMARY KEY,
    dish_id BIGINT NOT NULL REFERENCES dishes(id) ON DELETE CASCADE,
    spec_name VARCHAR(50) NOT NULL,
    spec_values JSONB NOT NULL -- [{"name":"大","price":5}, ...]
);

CREATE INDEX idx_dish_specs_dish ON dish_specs (dish_id);

-- =========================
-- 6. 购物车
-- =========================
CREATE TABLE carts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cart_items (
    id BIGSERIAL PRIMARY KEY,
    cart_id BIGINT NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    dish_id BIGINT NOT NULL REFERENCES dishes(id),
    quantity INT NOT NULL CHECK (quantity > 0),
    selected_specs JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cart_items_cart ON cart_items (cart_id);
CREATE INDEX idx_cart_items_dish ON cart_items (dish_id);

-- =========================
-- 7. 订单
-- =========================
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending/paid/completed/cancelled
    context_snapshot JSONB NOT NULL DEFAULT '{}',  -- 下单时环境快照
    address_snapshot JSONB NOT NULL DEFAULT '{}',  -- 地址冗余快照
    note VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_user_created ON orders (user_id, created_at DESC);
CREATE INDEX idx_orders_status ON orders (status);

CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    dish_id BIGINT NOT NULL REFERENCES dishes(id),
    dish_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price_snapshot DECIMAL(10,2) NOT NULL,
    selected_specs JSONB NOT NULL DEFAULT '{}',
    ai_metadata_snapshot JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX idx_order_items_order ON order_items (order_id);
CREATE INDEX idx_order_items_dish ON order_items (dish_id);

-- =========================
-- 8. AI 会话与消息（可追溯）
-- =========================
CREATE TABLE chat_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    summary VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_sessions_user ON chat_sessions (user_id, created_at DESC);

CREATE TABLE chat_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    recommended_dish_ids JSONB NOT NULL DEFAULT '[]', -- [101,102]
    candidate_dish_ids JSONB NOT NULL DEFAULT '[]',   -- 召回候选集（必须保留）
    meta JSONB NOT NULL DEFAULT '{}',                 -- 耗时/降级/过滤统计
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_messages_session_created ON chat_messages (session_id, created_at);

-- =========================
-- 9. 评价
-- =========================
CREATE TABLE reviews (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dish_id BIGINT NOT NULL REFERENCES dishes(id) ON DELETE CASCADE,
    order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    tags JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, order_id, dish_id)
);

CREATE INDEX idx_reviews_dish_created ON reviews (dish_id, created_at DESC);
CREATE INDEX idx_reviews_user_created ON reviews (user_id, created_at DESC);

-- =========================
-- 10. 偏好事件（画像可追溯）
-- =========================
CREATE TABLE preference_events (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(30) NOT NULL,  -- tag_init/manual_edit/order/review/chat_feedback
    payload JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pref_events_user_created ON preference_events (user_id, created_at DESC);
CREATE INDEX idx_pref_events_payload_gin ON preference_events USING GIN (payload);
