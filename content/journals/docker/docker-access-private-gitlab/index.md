---
title: "Dockerfile 如何設定 Golang 存取 Private GitLab"
date: 2026-01-19T14:40:07+08:00
draft: true
description: "本文介紹如何在 Dockerfile 中設定 Golang 以存取 Private GitLab 儲存庫。"
---

## 前言🔖

近期開始對公司內部幾個 API 服務進行 Docker 容器化，這些服務的程式碼都有使用共用的 Private GitLab 儲存庫。本文將分享如何在 Dockerfile 中設定 Golang，以便能夠順利存取這些 Private GitLab 儲存庫。

## 問題描述❓

一開始時，Dockerfile 如下所示：

```dockerfile
ARG GO_VERSION=1.22
ARG ALPINE_VERSION=3.18
ARG SERVICE_NAME=api
ARG SERVICE_PORT=9090
ARG SERVICE_CMD=api
ARG USER=sre
ARG TOKEN=your_token_here

# 階段 1: 構建階段
FROM golang:${GO_VERSION}-alpine AS builder

# 重新宣告 ARG 以在此階段使用
ARG SERVICE_NAME
ARG USER
ARG TOKEN

# 安裝必要的構建工具
RUN apk add --no-cache git make bash

# 設置工作目錄
WORKDIR /app

# 配置 Git 以使用內部 GitLab 儲存庫，https 替代 http
RUN git config --global url."https://private.gitlab.com/".insteadOf "http://private.gitlab.com/"

# 複製依賴文件
COPY go.mod go.sum ./

# 下載依賴
RUN go mod tidy -download -x

# 複製整個專案
COPY . .

# 創建輸出目錄並構建應用
RUN mkdir -p /app/bin && \
  CGO_ENABLED=0 GOOS=linux go build -o /app/bin/${SERVICE_NAME} main.go && \
  echo "Build completed. Checking output file:" && \
  ls -lh /app/bin/ && \
  test -f /app/bin/${SERVICE_NAME} || (echo "ERROR: Binary file not found!" && exit 1)

# 階段 2: 運行階段
FROM alpine:${ALPINE_VERSION}

# 重新宣告 ARG 以在此階段使用
ARG SERVICE_NAME
ARG SERVICE_PORT
ARG SERVICE_CMD

# 將 ARG 轉換為 ENV 以便運行時使用
ENV SERVICE_NAME=${SERVICE_NAME}
ENV SERVICE_PORT=${SERVICE_PORT}
ENV SERVICE_CMD=${SERVICE_CMD}

# 安裝 CA 證書和時區數據
RUN apk --no-cache add ca-certificates tzdata

# 創建非 root 用戶
RUN addgroup -g 1000 appuser && \
  adduser -D -u 1000 -G appuser appuser

# 設置工作目錄
WORKDIR /app

# 從構建階段複製可執行文件
COPY --from=builder --chown=appuser:appuser /app/bin/${SERVICE_NAME} ./${SERVICE_NAME}

# 創建日誌目錄
RUN mkdir -p logs && chown -R appuser:appuser logs

# 切換到非 root 用戶
USER appuser

# 暴露應用端口
EXPOSE ${SERVICE_PORT}

# 啟動應用
CMD ["sh", "-c", "./${SERVICE_NAME} ${SERVICE_CMD}"]
```

這份 Dockerfile 在某些情況下無法成功下載 Private GitLab 儲存庫中的依賴，導致構建失敗。後來詢問後端的 RD 同事，才知道需要在 Dockerfile 中設定 Golang 的私有倉庫環境變量，並且配置 Git 以使用帶有認證的 URL。才能夠順利存取 Private GitLab 儲存庫。

## 解決方案✅

修改後的 Dockerfile 如下所示：

```dockerfile
ARG GO_VERSION=1.22
ARG ALPINE_VERSION=3.18
ARG SERVICE_NAME=api
ARG SERVICE_PORT=9090
ARG SERVICE_CMD=api
ARG USER=sre
ARG TOKEN=your_token_here

# 階段 1: 構建階段
FROM golang:${GO_VERSION}-alpine AS builder

# 重新宣告 ARG 以在此階段使用
ARG SERVICE_NAME
ARG USER
ARG TOKEN

# 安裝必要的構建工具
RUN apk add --no-cache git make bash

# 設置工作目錄
WORKDIR /app

# 設置 Go 私有倉庫環境變量
RUN go env -w GOPRIVATE="private.gitlab.com" && \
  go env -w GONOSUMDB="private.gitlab.com" && \
  go env -w GONOPROXY="private.gitlab.com"

# 配置 Git 以使用內部 GitLab 儲存庫，https 替代 http
RUN git config --global url."https://${USER}:${TOKEN}@private.gitlab.com/".insteadOf "https://private.gitlab.com/" && \
  git config --global url."https://${USER}:${TOKEN}@private.gitlab.com/".insteadOf "http://private.gitlab.com/"

# 複製依賴文件
COPY go.mod go.sum ./

# 下載依賴
RUN go mod tidy -download -x

# 複製整個專案
COPY . .

# 創建輸出目錄並構建應用
RUN mkdir -p /app/bin && \
  CGO_ENABLED=0 GOOS=linux go build -o /app/bin/${SERVICE_NAME} main.go && \
  echo "Build completed. Checking output file:" && \
  ls -lh /app/bin/ && \
  test -f /app/bin/${SERVICE_NAME} || (echo "ERROR: Binary file not found!" && exit 1)

# 階段 2: 運行階段
FROM alpine:${ALPINE_VERSION}

# 重新宣告 ARG 以在此階段使用
ARG SERVICE_NAME
ARG SERVICE_PORT
ARG SERVICE_CMD

# 將 ARG 轉換為 ENV 以便運行時使用
ENV SERVICE_NAME=${SERVICE_NAME}
ENV SERVICE_PORT=${SERVICE_PORT}
ENV SERVICE_CMD=${SERVICE_CMD}

# 安裝 CA 證書和時區數據
RUN apk --no-cache add ca-certificates tzdata

# 創建非 root 用戶
RUN addgroup -g 1000 appuser && \
  adduser -D -u 1000 -G appuser appuser

# 設置工作目錄
WORKDIR /app

# 從構建階段複製可執行文件
COPY --from=builder --chown=appuser:appuser /app/bin/${SERVICE_NAME} ./${SERVICE_NAME}

# 創建日誌目錄
RUN mkdir -p logs && chown -R appuser:appuser logs

# 切換到非 root 用戶
USER appuser

# 暴露應用端口
EXPOSE ${SERVICE_PORT}

# 啟動應用
CMD ["sh", "-c", "./${SERVICE_NAME} ${SERVICE_CMD}"]
```

主要的修改點包括：

1. 設置 Go 私有倉庫環境變量：

   ```dockerfile
   RUN go env -w GOPRIVATE="private.gitlab.com" && \
     go env -w GONOSUMDB="private.gitlab.com" && \
     go env -w GONOPROXY="private.gitlab.com"
   ```

2. 配置 Git 以使用帶有認證的 URL：

   ```dockerfile
   RUN git config --global url."https://${USER}:${TOKEN}@private.gitlab.com/".insteadOf "https://private.gitlab.com/" && \
     git config --global url."https://${USER}:${TOKEN}@private.gitlab.com/".insteadOf "http://private.gitlab.com/"
    ```
