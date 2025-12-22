# AI 智能点餐系统（后端）技术文档（FastAPI + PostgreSQL + DeepSeek）

本文档面向**前端对接/联调/测试**，说明后端当前可用接口与数据格式（以现有 FastAPI 项目为准）。  
服务基于 FastAPI + SQLAlchemy Async + PostgreSQL，并集成 DeepSeek 作为 AI 推荐引擎。

---

## 1. 基本信息

- **服务框架**：FastAPI（ASGI，异步）
- **服务端口**：默认 `8000`
- **Swagger**：`http://127.0.0.1:8000/docs`
- **OpenAPI**：`http://127.0.0.1:8000/openapi.json`
- **数据库**：PostgreSQL（asyncpg）
- **鉴权**：JWT Bearer Token
- **AI**：DeepSeek Chat Completion（httpx）

---

## 2. 环境变量（.env）

在项目根目录创建 `.env`（推荐）：

```env
# 数据库（必须）
DATABASE_URL=postgresql+asyncpg://ai_user:1234@127.0.0.1:5432/ai_order

# JWT（推荐）
JWT_SECRET=change-me
JWT_EXPIRE_MINUTES=10080

# DeepSeek（AI 推荐必须）
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

> 注意：DeepSeek Key 必须**非空**，且建议去除首尾空格/换行（后端应 `.strip()`）。

---

## 3. 鉴权（JWT Bearer）

### 3.1 获取 Token

注册或登录成功后返回：

```json
{
  "user_id": 1,
  "access_token": "xxxxx.yyyyy.zzzzz",
  "token_type": "bearer"
}
```

### 3.2 发送 Token

所有带 🔒 的接口需要在请求头携带：

```
Authorization: Bearer <access_token>
```

### 3.3 Swagger 中如何填

打开 `/docs`，点击右上角 **Authorize**（锁图标），输入：

```
Bearer <access_token>
```

---

## 4. 数据库核心表（概览）

> 以 init.sql 为准，以下字段是后端逻辑强依赖的核心集合。

### 4.1 users（用户）

- `id` BIGSERIAL PK
- `username` VARCHAR UNIQUE
- `password_hash` VARCHAR
- `phone` VARCHAR
- `created_at` TIMESTAMP

### 4.2 user_preferences（用户画像）

- `user_id` PK/FK
- `explicit_tags` JSONB（用户显式标签）
- `implicit_profile` JSONB（系统推断画像）
- `dietary_restrictions` JSONB（忌口）
- `last_updated`

### 4.3 user_addresses（地址）

- `id` BIGSERIAL PK
- `user_id` FK
- `contact_name`
- `phone`
- `address_line`
- `is_default`

### 4.4 categories / dishes / dish_specs（菜单域）

- `categories(id,name,sort_order)`
- `dishes(id,category_id,name,description,price,image_url,status,ai_metadata,sales_count,rating_avg)`
- `dish_specs(id,dish_id,spec_name,spec_values)`

其中 `dishes.ai_metadata` 是 AI 决策元数据（JSONB），例如口味、食材、温度、场景、营养等。

### 4.5 orders / order_items（订单域）

- `orders(id,user_id,total_amount,status,context_snapshot,note,created_at,...)`
- `order_items(id,order_id,dish_id,dish_name,quantity,price_snapshot,selected_specs)`

### 4.6 reviews（评价）

- `reviews(id,user_id,dish_id,order_id,rating,comment,tags,created_at)`

### 4.7 chat_sessions / chat_messages（AI 会话）

- `chat_sessions(id,user_id,summary,created_at)`
- `chat_messages(id,session_id,role,content,recommended_dish_ids,created_at)`

---

## 5. API 约定

- 统一前缀：`/api`
- 参数校验失败：`422 Unprocessable Entity`（FastAPI/Pydantic 默认）
- 鉴权失败：通常 `401/403`
- 业务错误：通常 `400`（`detail` 为字符串或结构化对象）
- 未处理异常：`500`（应逐步消除）

---

## 6. 接口文档（当前可用）

> 说明：你当前版本**没有 pay/cancel 等订单状态流转接口**，因此本文档不包含此类接口。订单状态目前以创建时写入为准（如 `pending`）。

### 6.1 Auth（认证）

#### 6.1.1 注册

- **POST** `/api/auth/register`

Request Body：

```json
{
  "username": "u123",
  "password": "123456",
  "phone": "13800000000"
}
```

Response 200：

```json
{
  "user_id": 1,
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

常见错误：

- 422：字段缺失或类型错误
- 400：用户名已存在（若后端启用此校验）

---

#### 6.1.2 登录

- **POST** `/api/auth/login`

Request Body：

```json
{
  "username": "u123",
  "password": "123456"
}
```

Response 200：

```json
{
  "user_id": 1,
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

---

### 6.2 Users（用户）

#### 6.2.1 当前用户信息

- 🔒 **GET** `/api/users/me`

Response 200（示例）：

```json
{
  "id": 1,
  "username": "u123",
  "phone": "13800000000",
  "created_at": "2025-12-22T14:00:00"
}
```

---

#### 6.2.2 获取画像

- 🔒 **GET** `/api/users/preferences`

Response 200（示例）：

```json
{
  "explicit_tags": ["light", "seafood"],
  "implicit_profile": {"price_sensitivity": "low"},
  "dietary_restrictions": ["香菜"]
}
```

---

#### 6.2.3 更新画像

- 🔒 **PUT** `/api/users/preferences`

Request Body（示例）：

```json
{
  "explicit_tags": ["light", "seafood"],
  "dietary_restrictions": ["香菜"]
}
```

Response 200：

```json
{
  "ok": true
}
```

---

### 6.3 Addresses（地址）

#### 6.3.1 地址列表

- 🔒 **GET** `/api/addresses`

Response 200（示例）：

```json
[
  {
    "id": 1,
    "contact_name": "张三",
    "phone": "13800000000",
    "address_line": "北京市朝阳区xxx",
    "is_default": true
  }
]
```

---

#### 6.3.2 新增地址

- 🔒 **POST** `/api/addresses`

Request Body：

```json
{
  "contact_name": "张三",
  "phone": "13800000000",
  "address_line": "北京市朝阳区xxx"
}
```

Response 200（示例）：

```json
{
  "id": 1
}
```

---

#### 6.3.3 设为默认地址

- 🔒 **POST** `/api/addresses/{address_id}/set-default`

Response 200：

```json
{
  "ok": true
}
```

---

### 6.4 Dishes（菜单）

#### 6.4.1 分类

- **GET** `/api/dishes/categories`

Response 200（示例）：

```json
[
  {"id": 1, "name": "热菜"},
  {"id": 2, "name": "主食"}
]
```

---

#### 6.4.2 菜品列表

- **GET** `/api/dishes`

可能支持的 Query（以 OpenAPI 为准）：

- `category_id`
- `q`（关键词）
- `status`

Response 200（示例）：

```json
[
  {
    "id": 1,
    "category_id": 1,
    "name": "清蒸虾",
    "price": 58.0,
    "status": "on_sale",
    "sales_count": 10,
    "ai_metadata": {
      "taste": ["light"],
      "ingredients": ["shrimp"],
      "temperature": "hot",
      "scene": ["dinner"],
      "nutrition": {"protein": "high"}
    }
  }
]
```

---

#### 6.4.3 菜品详情

- **GET** `/api/dishes/{dish_id}`

Response 200（示例）：

```json
{
  "id": 1,
  "name": "清蒸虾",
  "price": 58.0,
  "description": "…",
  "ai_metadata": { "taste": ["light"], "ingredients": ["shrimp"] },
  "specs": [
    {
      "spec_name": "辣度",
      "spec_values": [{"name":"不辣","delta":0},{"name":"微辣","delta":0}]
    }
  ]
}
```

---

### 6.5 Cart（购物车）

> 如果你的 Swagger 已出现 cart 相关接口，则按以下格式对接。

#### 6.5.1 购物车详情

- 🔒 **GET** `/api/cart`

Response 200（示例）：

```json
{
  "items": [
    {
      "item_id": 1,
      "dish_id": 1,
      "quantity": 2,
      "selected_specs": {"辣度": "不辣"}
    }
  ]
}
```

---

#### 6.5.2 加入购物车

- 🔒 **POST** `/api/cart/items`

Request Body：

```json
{
  "dish_id": 1,
  "quantity": 2,
  "selected_specs": {"辣度": "不辣"}
}
```

Response 200（示例）：

```json
{
  "item_id": 1
}
```

---

#### 6.5.3 修改购物车项

- 🔒 **PUT** `/api/cart/items/{item_id}`

Request Body：

```json
{
  "quantity": 3,
  "selected_specs": {"辣度": "微辣"}
}
```

Response 200：

```json
{
  "ok": true
}
```

---

#### 6.5.4 删除购物车项

- 🔒 **DELETE** `/api/cart/items/{item_id}`

Response 200：

```json
{
  "ok": true
}
```

---

### 6.6 Orders（订单）

#### 6.6.1 创建订单

- 🔒 **POST** `/api/orders`

Request Body（示例）：

```json
{
  "address_id": 1,
  "note": "不要香菜",
  "items": [
    {"dish_id": 1, "quantity": 2, "selected_specs": {"辣度": "不辣"}},
    {"dish_id": 2, "quantity": 1, "selected_specs": {}}
  ]
}
```

Response 200（示例）：

```json
{
  "id": 1,
  "status": "pending",
  "total_amount": 129.0,
  "created_at": "2025-12-22T15:00:00"
}
```

业务校验（建议/通常实现）：

- `items` 不能为空
- `address_id` 必须存在且属于当前用户
- `dish_id` 必须存在且 `status=on_sale`

---

#### 6.6.2 订单列表

- 🔒 **GET** `/api/orders`

Response 200（示例）：

```json
[
  {
    "id": 1,
    "status": "pending",
    "total_amount": 129.0,
    "created_at": "2025-12-22T15:00:00"
  }
]
```

---

#### 6.6.3 订单详情

- 🔒 **GET** `/api/orders/{order_id}`

Response 200（示例）：

```json
{
  "id": 1,
  "status": "pending",
  "total_amount": 129.0,
  "note": "不要香菜",
  "items": [
    {
      "dish_id": 1,
      "dish_name": "清蒸虾",
      "quantity": 2,
      "price_snapshot": 58.0,
      "selected_specs": {"辣度": "不辣"}
    }
  ]
}
```

---

### 6.7 Reviews（评价）

#### 6.7.1 创建评价

- 🔒 **POST** `/api/reviews`

Request Body：

```json
{
  "order_id": 1,
  "dish_id": 1,
  "rating": 5,
  "comment": "清淡好吃，虾很新鲜",
  "tags": ["light", "seafood"]
}
```

Response 200（示例）：

```json
{
  "id": 1
}
```

建议约束（若已实现则前端必须遵守）：

- order 必须属于当前 user
- dish 必须属于该 order
- 可按业务要求限制：仅当订单完成才允许评价（你当前未提供订单状态流转接口时，可先不启用此限制）

---

#### 6.7.2 某菜品的评价列表

- **GET** `/api/reviews/dish/{dish_id}`

Response 200（示例）：

```json
[
  {
    "id": 1,
    "rating": 5,
    "comment": "清淡好吃，虾很新鲜",
    "tags": ["light", "seafood"],
    "created_at": "2025-12-22T15:10:00"
  }
]
```

---

#### 6.7.3 我的评价（如实现）

- 🔒 **GET** `/api/reviews/me`

Response 200（示例）：

```json
[
  {
    "id": 1,
    "dish_id": 1,
    "rating": 5,
    "comment": "…",
    "created_at": "..."
  }
]
```

---

### 6.8 AI（DeepSeek 推荐）

#### 6.8.1 发送消息（会话内）

- 🔒 **POST** `/api/ai/sessions/{session_id}/messages`

**请求体格式**以 Swagger 显示为准：如果 schema 显示为 `string`，则直接传 JSON 字符串。

示例（纯字符串）：

```json
"我想吃点清淡的，最好有虾"
```

Response 200（推荐标准化结构，具体字段以你实现为准）：

```json
{
  "reply": "建议你尝试清蒸虾、虾仁豆腐等清淡海鲜类菜品。",
  "recommendations": [1, 5, 9],
  "meta": {
    "time_bucket": "dinner",
    "used_tags": ["light", "seafood"]
  }
}
```

**强约束（固定决策）**

- `recommendations` 必须**只能从候选菜品集合中选择**（候选集通常为 `dishes.status=on_sale`，可叠加其它过滤规则）。

---

## 7. 端到端联调建议顺序（当前版本）

> 不包含 pay/cancel（因为你当前没有这些接口）。

1. 注册/登录 → 获取 Token  
2. 设置 Swagger Authorize（Bearer Token）  
3. 创建地址（POST /api/addresses）并设默认（set-default）  
4. 拉取菜品列表（GET /api/dishes）确认 dish_id 可用  
5. 创建订单（POST /api/orders）  
6. 创建评价（POST /api/reviews）  
7. AI 推荐（POST /api/ai/sessions/{session_id}/messages）

---

## 8. 常见问题排查

### 8.1 `Illegal header value b'Bearer '`

表示 DeepSeek Key 为空，通常原因：

- `.env` 没有 `DEEPSEEK_API_KEY`
- 启动 uvicorn 的 shell 没加载 `.env`（或 config 未 `load_dotenv()`）
- Key 值带换行/空格导致最终为空（应 `.strip()`）

### 8.2 422 Unprocessable Entity

Pydantic 参数校验失败：

- 请求体缺字段
- 类型不匹配（比如 `address_id` 传了字符串）
- JSON 结构不符合 schema

### 8.3 401/403

Token 未设置或过期：

- 确认 Swagger 已 Authorize
- 请求头必须 `Authorization: Bearer <token>`

---

## 9. 附录：订单 items 字段规范

`POST /api/orders` 的 `items` 推荐统一为如下 JSON 结构：

```json
{
  "dish_id": 1,
  "quantity": 2,
  "selected_specs": {"辣度": "不辣"}
}
```

后端将以此生成 `order_items`，并写入：

- `dish_name`（冗余快照）
- `price_snapshot`（下单价格快照）
- `selected_specs`（规格快照）

---

以上为当前后端接口与数据格式说明。最终以 `/openapi.json` 为准。
