# clothDiy 项目开发任务清单

> 本文件可被 Multi-Agent Framework 直接读取执行：
> `python main.py --file tasks/clothdiy_tasks.md`


## 用户登录注册模块 - 需求分析

### 背景
clothDiy 是服装DIY定制小程序，用户端为微信小程序。

### 需求描述
设计用户登录注册模块的需求规格，包含：
- 微信一键登录（微信开放平台，获取 unionid）
- 手机号+验证码登录
- 账号密码登录（可选）
- 用户注册流程（首次微信登录自动注册）
- Token 刷新机制（JWT，7天有效期）
- 登录态过期处理（静默刷新 vs 强制重新登录）

输出格式：PRD 文档，包含用户故事、流程图、接口清单。

### 指定 Agent
product_manager


## 用户登录注册模块 - 数据库设计

### 需求背景
承接上一个需求分析，设计数据库表结构。

### 设计内容
设计用户登录注册模块的数据库表结构，使用 PostgreSQL：

- `users` 用户主表（id, openid, unionid, phone, nickname, avatar, created_at）
- `wechat_bind` 微信绑定表（支持多平台：微信小程序/公众号/开放平台）
- `sms_codes` 短信验证码记录表（phone, code, purpose, expires_at, used）
- `login_logs` 登录日志表（user_id, ip, device, os, login_at）

输出：完整 CREATE TABLE SQL + GORM Model Go 代码。

### 指定 Agent
database_eng


## 用户登录注册模块 - Go后端API

### 上下文
clothDiy_go_api 项目，已集成 Gin + GORM + PostgreSQL + Redis。
数据库设计已完成（见上方任务）。

### 开发内容
实现以下 API 接口：

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 微信登录 | POST | /api/v1/auth/wechat-login | code换session，自动注册/登录 |
| 验证码登录 | POST | /api/v1/auth/sms-login | phone + code |
| 密码登录 | POST | /api/v1/auth/password-login | phone + password |
| 发送验证码 | POST | /api/v1/auth/send-sms | 频率限制：1分钟1次，24小时5次 |
| 刷新Token | POST | /api/v1/auth/refresh-token | RefreshToken换新的AccessToken |
| 登出 | POST | /api/v1/auth/logout | 使Redis中的Token失效 |

JWT 认证中间件，错误码规范。

### 指定 Agent
go_backend_dev


## 小程序端登录页面

### 上下文
clothDiy_miniprogram 微信小程序项目，使用 VantWeapp 组件库。
已集成 Three.js 小程序适配版。

### 开发内容
实现小程序登录页面（pages/login/）：

1. 首选：微信一键登录按钮（wx.login 获取 code）
2. 备选：手机号+验证码登录表单
3. 注册扩展表单（首次登录时采集：身高/体重/性别，用于初始化3D人体模型）
4. 登录成功后：跳转首页，同时加载用户3D模型预览（Three.js Canvas）

UI 风格：Fashion-Tech，简洁白色为主，强调色 #FF6B6B。

### 指定 Agent
miniprogram_dev


## SMPL-X 体型参数映射算法

### 需求描述
实现厘米级体型参数到 SMPL-X β 参数的映射函数。

**输入参数（9维）：**
身高(cm)、体重(kg)、胸围(cm)、腰围(cm)、臀围(cm)、肩宽(cm)、臂长(cm)、腿长(cm)、性别(0/1)

**输出：**
SMPL-X 的 β 参数（10维，PCA主成分）

**要求：**
1. 建立线性回归模型（基于统计人体数据库）
2. 实现反向映射（β → 体型测量值）
3. 支持自定义体型微调（每个维度 ±2σ 范围）
4. 输出 Go 版本（后端用）和 TypeScript 版本（前端用）
5. 包含单元测试

### 指定 Agent
three_graphics_eng


## 3D服装展示页面 - 小程序前端

### 上下文
依赖 SMPL-X 映射算法已完成。
clothDiy_miniprogram 项目。

### 开发内容
实现小程序的3D服装展示页面（pages/showcase/）：

功能：
1. 加载 .glb/.gltf 格式的3D服装模型（使用 Three.js 小程序版）
2. 手势操作：单指旋转、双指缩放、双指平移
3. 实时应用 SMPL-X 体型参数变形（MorphTargets）
4. 面料纹理动态替换（UV映射，支持上传自定义图案）
5. 多角度截图分享（Canvas.toTempFilePath）
6. 服装颜色/尺码选择

性能要求：
- 首帧渲染 < 2s
- Draco 压缩（.glb 文件 < 5MB）
- LOD 分级加载（近距离高精度，远距离低精度）

### 指定 Agent
miniprogram_dev


## 订单管理模块 - 完整开发

### 需求描述
完整开发订单管理模块（后端 + 数据库 + API）。

**数据库设计：**
- `orders` 订单主表
- `order_quotes` 工厂报价表
- `production_progress` 生产进度表
- `order_status_logs` 状态变更日志表

**订单状态机：**
待报价 → 已报价 → 已确认 → 生产中 → 已完成
    ↓（拒绝）    ↓（取消）   ↓（取消）
  已拒绝       已取消     已取消

**API 接口：**
- POST /api/v1/orders（用户下单）
- GET /api/v1/orders（订单列表，分页筛选）
- GET /api/v1/orders/:id（订单详情）
- POST /api/v1/orders/:id/quote（工厂提交报价）
- POST /api/v1/orders/:id/confirm（用户确认报价）
- POST /api/v1/orders/:id/cancel（取消订单）
- GET /api/v1/orders/:id/progress（查询生产进度）
- POST /api/v1/orders/:id/progress（工厂更新生产进度）

### 指定 Agent
go_backend_dev
