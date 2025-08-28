---
title: "使用 golang 實現 WebSocket 聊天室練習"
date: 2025-08-27T09:19:34+08:00
draft: true
---
## 前言

近期因為工作的需求，SRE 開始要用 golang 開發一些平台應用工具的 API。因為之前沒有接觸 golang，所以決定從一個簡單的 WebSocket 聊天室開始練習。

建立一個簡單的聊天室，主要包含以下幾個步驟：

1. 建立 WebSocket 伺服器
2. Client 連接 WebSocket 伺服器
3. Server 處理來自 Client 的訊息與回應
4. Client 處理來自 Server 的訊息與回應

## 建立 WebSocket 伺服器

這次使用的是 `gorilla/websocket` 套件來實現 WebSocket 伺服器。

```go
package main

import (
 "net/http"

 "github.com/gin-gonic/gin"
 "github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
  // 檢查請求來源設置 true，僅能在開發測試過程中使用
 CheckOrigin: func(r *http.Request) bool {
  return true
 },
}

var (
  clients   = make(map[*websocket.Conn]bool) // 連接的客戶端
  broadcast = make(chan Message)             // 廣播訊息的通道
)

func handleConnection(w http.ResponseWriter, r *http.Request) {
 conn, err := upgrader.Upgrade(w, r, nil)
 if err != nil {
  fmt.Println("Error while upgrading connection:", err)
  return
 }
 defer conn.Close()

 for {
  messageType, msg, err := conn.ReadMessage()
  if err != nil {
   fmt.Println("Error while reading message:", err)
   break
  }
  fmt.Printf("Received message: %s\n", msg)

  err = conn.WriteMessage(messageType, msg)
  if err != nil {
   fmt.Println("Error while writing message:", err)
   break
  }
 }
}

func main() {
 http.HandleFunc("/ws", handleConnection)
 err := http.ListenAndServe(":8080", nil)
 if err != nil {
  fmt.Println("Error while starting server:", err)
 }
}
```
