---
title: "使用 Docker 搭建 MongoDB"
date: 2026-01-29T11:58:09+08:00
draft: false
tags: ["docker"]
description: "本文介紹如何使用 Docker 搭建 MongoDB 環境，包括配置副本集和設置持久化存儲。"
---

## 前言🔖

近期因為測試需求，需要在本地搭建一個 MongoDB 環境。考慮到方便性和可移植性，我決定使用 Docker 來搭建這個環境。本文將詳細介紹如何使用 Docker 搭建 MongoDB，包括配置副本集和設置持久化存儲。

## Docker Compose 配置文件📄

首先，我們需要創建一個 `docker-compose.yaml` 文件來定義 MongoDB 服務。以下是我們的配置文件內容：

```yaml
version: "3.8"

services:
  mongodb:
    image: mongo:8.0.3
    container_name: mongodb
    restart: always
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: rootpassword
    command: >
      mongod
      --replSet rs0
      --bind_ip 0.0.0.0
      --wiredTigerCacheSizeGB 3
      --keyFile /data/mongodb.key
    volumes:
      - ./data:/data/db
      - ./configdb:/data/configdb
      - ./mongodb.key:/data/mongodb.key:ro
    networks:
      - mongoNet

networks:
  mongoNet:
    driver: bridge
```

mongodb 的版本選擇了 8.0.3，並且設置了管理員帳號和密碼。為了確保數據的持久化，我們將數據目錄映射到本地的 `./data` 和 `./configdb` 目錄。此外，我們還使用了一個密鑰文件 `mongodb.key` 來配置副本集的安全性。

`--replSet rs0` 參數用於啟用副本集功能，將副本集名稱設置為 `rs0`。。副本集是 MongoDB 提供高可用性和資料冗餘的機制，它會在多個伺服器之間自動複製資料。

`--bind_ip 0.0.0.0` 參數允許 MongoDB 接受來自任何 IP 地址的連接，這對於在 Docker 容器中運行的服務非常重要。

`--wiredTigerCacheSizeGB 3` 參數設置了 WiredTiger 存儲引擎的緩存(記憶體快取)大小為 3GB，這有助於提升性能。

`--keyFile /data/mongodb.key` 參數指定了用於副本集成員之間身份驗證的密鑰文件路徑。

## 創建密鑰文件🔐

在啟動 MongoDB 容器之前，我們需要創建一個密鑰文件 `mongodb.key`。這個文件將用於副本集成員之間的身份驗證。可以使用以下命令生成一個隨機的密鑰文件：

```bash
# 生成 keyfile（至少 6 個字符，最多 1024 個字符）
openssl rand -base64 756 > mongodb.key

# 設置正確的權限（必須是 400 或 600）
chmod 400 mongodb.key

# 如果需要在 Docker 中使用，確保所有者正確
sudo chown 999:999 mongodb.key
```

## 問題排查❓

如果在啟動容器後遇到錯誤日誌，先確認 `mongodb.key` 文件的權限是否正確設置為 999:999，並且權限為 400 或 600。這是因為 MongoDB 需要確保密鑰文件的安全性。

```log
Error creating service context","attr":{"error":"Location5579201: Unable to acquire security key[s]
```

## 測試連接🔌

可以使用 MongoDB 客戶端工具或進入容器內部來測試連接：

```bash
# 進入容器
docker exec -it mongodb mongosh -u root -p rootpassword --authenticationDatabase admin

# 或直接連接
mongosh mongodb://root:rootpassword@localhost:27017/
```

## 參考文獻📚

- [官方 MongoDB Docker 建置指南](https://www.mongodb.com/resources/products/compatibilities/docker)
