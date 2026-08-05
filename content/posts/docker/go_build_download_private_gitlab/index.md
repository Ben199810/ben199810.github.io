---
title: "Docker 建構 Golang 專案時，下載私有庫依賴失敗"
date: 2026-01-19T14:40:07+08:00
draft: false
tags: ["Docker", "Golang"]
description: "在進行 Golang 專案建構時，`go.mod` 可能會需要指定在同一個私有庫中的其他專案作為依賴。在建構的過程中如果遇到無法下載私有庫依賴的問題，可能會導致建構的過程中失敗！本文將介紹如何解決這個問題。"
---

## 問題描述❓

在進行 Golang 專案建構時，`go.mod` 可能會需要指定在同一個私有庫中的其他專案作為依賴。在建構的過程中如果遇到無法下載私有庫依賴的問題，可能會導致建構的過程中失敗！

```
module project

go 1.24.2

require (
	github.com/go-sql-driver/mysql v1.9.3
	github.com/redis/go-redis/v9 v9.18.0
	private.gitlab.com/golibrary/module v1.0.34
)

require (
	cloud.google.com/go/auth v0.15.0 // indirect
	cloud.google.com/go/auth/oauth2adapt v0.2.7 // indirect
	cloud.google.com/go/compute/metadata v0.6.0 // indirect
)
```

{{< mermaid >}}
flowchart LR

subgraph private_network[Private Network]
subgraph private_gitlab[Private GitLab]
golang_projcet[Golang 專案]
golang_module_project[Golang Module 專案]

golang_projcet -->|go.mod| golang_module_project
end
end
{{< /mermaid >}}

這是因為私有 GitLab 通常會有防火牆或是需要認證的限制，如果直接使用 `go get` 或 `go mod tidy` Golang 會嘗試去抓公開的 Proxy 伺服器，導致訪問私有 GitLab 失敗，進而導致無法下載私有庫依賴。

下面是 Golang 在建構專案時，下載私有庫依賴失敗的流程圖:

{{< mermaid >}}
flowchart LR

subgraph CICD[CI/CD Pipeline]
A[執行 go get / go build] --> B{Go 判斷模組路徑}
B -->|未設定 GOPRIVATE| C[走公開 GOPROXY]
C --> D[回報 404 / 410 錯誤]
D --> E[下載失敗 ❌]
B -->|已設定 GOPRIVATE| F[繞過 Proxy 直連 Git 伺服器]
F --> G{檢查 Git 驗證機制}
G -->|HTTPS 驗證失敗| H[提示輸入帳密或 Token 錯誤]
G -->|SSH 密鑰未設定/無權限| I[提示 Permission denied]
H --> E
I --> E
%% 解決方案分支
F -->|設定正確的憑證/SSH insteadOf| J[成功下載私有庫依賴 ✅]
style E fill:#f96,stroke:#333,stroke-width:2px
style J fill:#9f9,stroke:#333,stroke-width:2px

end

{{< /mermaid >}}

可以知道問題的癥結點在於要正確的設定 Golang 的私有倉庫環境變量，並且配置 Git 以使用帶有認證的 URL。這樣才能夠順利存取 Private GitLab 儲存庫。

## 解決方案✅

服務的建構工具使用 Dockerfile，所以會使用 Dockerfile 當作範例。

```dockerfile
ARG GO_VERSION=1.22
ARG ALPINE_VERSION=3.18

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

# 配置 Git，使用帶有認證的 URL
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

正確配置以後，Golang 專案在建構時就能夠順利下載私有庫依賴！

## 參考文獻📚

- [Golang 從私有的GitLab取得依賴module Unable to get modules from private gitlab repository](https://matthung0807.blogspot.com/2021/07/go-unable-to-get-modules-from-private-gitlab-repository.html)
