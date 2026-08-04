---
title: "使用 golang 實現 WebSocket 聊天室練習"
date: 2025-08-27T09:19:34+08:00
draft: true
---
## 前言

近期因為工作的需求，SRE 開始要用 golang 開發一些平台應用工具的 API。因為之前沒有接觸 golang，所以決定從一個簡單的 WebSocket 聊天室開始練習。

## 實體資料

一般會需要使用者註冊資料再登入，所以結構體需要定義出 User 所會需要的欄位。

```go
package entity

import (
 "time"

 "github.com/google/uuid"
)

type User struct {
 ID          uuid.UUID  `json:"id"`
 Username    string     `json:"username"`
 Email       string     `json:"email"`
 Password    string     `json:"-"` // 不序列化密碼
 CreatedAt   time.Time  `json:"created_at"`
 UpdatedAt   time.Time  `json:"updated_at"`
 LastLoginAt *time.Time `json:"last_login_at,omitempty"` // 最後登入時間，可能為空
}
```
