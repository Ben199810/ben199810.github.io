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
