---
title: "Redis Cli"
date: 2026-09-14T09:11:48+08:00
draft: true
description: ""
---

## 前言 🔖

Redis CLI 是用來與 Redis 伺服器進行互動的命令行工具。它允許用戶執行各種 Redis 命令，管理數據庫，並進行測試和調試。這篇文章主要會記錄我在日常工作常用的 Redis CLI 命令和技巧。

## 基本命令 📌

### 連接到 Redis 伺服器

最一開始，我們需要跟 Redis 建立連接以後才可以操作：

```bash
redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} -a ${REDIS_PASSWORD}
```

就像是登入資料庫一樣，需要帶入主機地址、端口號和密碼才能成功連接。連接的對象是 Redis Cluster。可以使用 `-c` 參數來啟用集群模式：

在群集模式下，Redis CLI 會自動處理節點之間的重定向，讓你可以像操作單節點 Redis 一樣操作整個集群。

```bash
redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT} -a ${REDIS_PASSWORD} -c
```

### 鍵

Redis 是鍵值對（key-value）的數據庫，每個鍵都是唯一的，並且可以對應一個值。通常，我們會使用一些基本命令來操作鍵，例如：

1. 查詢

    通常想要看全部的鍵，可以使用 `KEYS` 命令：

    ```bash
    KEYS *
    ```

    但是需要注意的是，`KEYS` 如果返回大量的鍵，可能會對 Redis 的性能造成影響。所以如果你知道鍵的模式，建議使用帶有模式的 `KEYS` 命令，例如：

    ```bash
    KEYS user:*
    ```

    這樣一來就可以避免對 Redis 性能造成過大的影響。

2. 檢查 Key 是否存在

    可以使用 `EXISTS` 命令來檢查某個鍵是否存在：

    ```bash
    EXISTS user:1001
    ```

    如果返回 `1`，表示鍵存在；如果返回 `0`，表示鍵不存在。

3. 查看 Key 的值
    可以使用 `GET` 命令來查看某個鍵的值：

    ```bash
    GET user:1001
    ```

    如果返回對應的值，表示鍵存在並且有值；如果返回 `nil`，表示鍵不存在或沒有值。

3. 新增 Key 與設置值

    可以使用 `SET` 命令來新增一個鍵：

    ```bash
    SET user:1001 "John Doe"
    ```

    如果返回 `OK`，表示鍵被成功新增。

4. 刪除 Key

    可以使用 `DEL` 命令來刪除某個鍵：

    ```bash
    DEL user:1001
    ```

    如果返回 `1`，表示鍵被成功刪除；如果返回 `0`，表示鍵不存在。

5. 查看 Key 的類型

    可以使用 `TYPE` 命令來查看某個鍵的類型：

    ```bash
    TYPE user:1001
    ```

    如果返回 `string`，表示鍵的類型是字符串；如果返回 `none`，表示鍵不存在。