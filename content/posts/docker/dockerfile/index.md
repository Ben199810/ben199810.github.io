---
title: "Dockerfile"
date: 2023-08-27
draft: false
description: "dockerfile 相關知識"
tags: ["docker"]

---

## Dockerfile

Dockerfile 是 Docker 的核心組件之一，用來定義如何建構一個 Docker 映像檔（image）。它是一個文本文件，包含了一系列的指令和參數，這些指令告訴 Docker 如何從基礎映像開始，安裝必要的軟體、配置環境變數、複製檔案等。

可以保證每次使用相同的 Dockerfile 建構出來的映像檔都是一致的，這對於部署和維護應用程式非常重要。

這裡要注意 EXPOSE，它用來告訴 Docker 哪些端口需要暴露給外部訪問。但是還是必須要在 `docker run` 時使用 `-p` 選項來實際映射端口。

```dockerfile
# 基礎映像，這裡使用 Alpine Linux，如果沒有指定 tag，則默認使用 latest
FROM alpine
# 設定作者資訊
LABEL maintainer="bing-wei"
# 設定工作目錄
WORKDIR /app
# 複製當前目錄下的所有檔案到容器的 /app 目錄
COPY . .
# 安裝必要的套件
RUN apk add --no-cache python3 py3-pip
# 安裝 Python 相依套件
RUN pip3 install -r requirements.txt
# 設定環境變數
ENV PYTHONUNBUFFERED=1
# 暴露容器的 8000 端口
EXPOSE 8000
# 設定容器啟動時執行的命令
CMD ["python3", "app.py"]
```

## 多階段建構

在實際的生產環境中，通常會使用多階段建構（multi-stage builds）來減少最終映像檔的大小，這樣可以在開發階段安裝所有必要的工具和依賴，但在最終映像檔中只保留運行應用程式所需的部分。

```dockerfile
# 第一階段：建構階段
FROM node:14 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
# 第二階段：運行階段
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 安全性考量

在撰寫 Dockerfile 時，還需要考慮安全性問題，例如：

- 使用官方的基礎映像，這樣可以減少安全漏洞的風險。
- 避免使用 `latest` 標籤，因為這樣會導致映像檔在不同時間點可能有不同的內容，應該使用具體的版本號。
- 建立帳號和設定權限，避免使用 root 帳號運行應用程式。

```dockerfile
# 使用官方的 Node.js 映像
FROM node:14
# 建立一個非 root 使用者
RUN useradd -m appuser
# 切換到非 root 使用者
USER appuser
# 設定工作目錄
WORKDIR /home/appuser/app
# 複製 package.json 和 package-lock.json
COPY package*.json ./
# 安裝相依套件
RUN npm install --only=production
# 複製應用程式檔案
COPY --chown=appuser:appuser . .
# 暴露應用程式端口
EXPOSE 3000
# 設定容器啟動命令
CMD ["npm", "start"]
```
