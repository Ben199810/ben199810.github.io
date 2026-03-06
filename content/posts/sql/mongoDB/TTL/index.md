---
title: "mongoDB TTL Index 自動刪除過期資料"
date: 2026-03-06T17:12:53+08:00
draft: false
tags: ["mongoDB", "TTL Index", "過期資料", "自動刪除", "資料庫管理"]
description: "在 MongoDB 中，TTL（Time To Live）索引是一種特殊的索引類型，用於自動刪除過期的文檔。這對於需要定期清理過期數據的應用程序非常有用，例如會話管理、日誌記錄和緩存數據等。本文將介紹 TTL 索引的概念、如何在程式碼中使用它，以及一些補充說明。"
---
## 前言🔖

目前在公司內部有 API 服務使用 mongoDB 並且這個 DB 並沒有託付給 DBA 管理，是由 SRE 自己管理的。因此對於這個 DB 的使用上有觀察到磁碟空間的使用有往上升且沒有下降的趨勢。已經觸發了監控告警的上限。因此研究了 mongoDB 的 TTL Index 機制。能有效的節省機器的效能以及控制成本。

## 什麼是超時索引❓

mongoDB 中有一種索引叫做`超時索引` ，用來自動清除過期的資料。超時索引的主要特點包括：

1. 自動過期：不需要手動處理過期文件，MongoDB 會自動處理。
2. 高效性：通過超時索引，MongoDB 可以高效地定期刪除過期文件，減少了性能開銷。
3. 適用於日誌和緩存：超時索引特別適用於存儲日誌數據、緩存數據和其他需要定期清理的情況。
4. 靈活設置：您可以根據需要設置不同的超時時間，以滿足不同數據的需求。

## 如何在程式碼中新增 TTL❓

假設我們有一個名為 "session" 的集合，用於存儲用戶會話信息。我們希望自動刪除超過一小時未活動的會話。

首先，在插入會話文檔時，我們需要添加一個 "expiry" 欄位，該欄位表示會話的過期時間。

```python
import pymongo
from datetime import datetime, timedelta

# 建立到MongoDB的連線
client = pymongo.MongoClient("mongodb://localhost:27017/")

# 選擇要建立索引的資料庫和集合
db = client["mydatabase"]
collection = db["session"]

# 插入一個會話文檔，並設定過期時間為一小時後
expiry_time = datetime.now() + timedelta(hours=1)
session_data = {
    "user_id": 123,
    "session_token": "abc123",
    "expiry": expiry_time
}
collection.insert_one(session_data)

# 關閉連線
client.close()
```

接下來，我們需要建立一個超時索引，以便自動刪除過期的會話文檔。我們將在 "expiry" 欄位上建立索引，並設置超時時間為一小時：

```python
# 在 "expiry" 欄位上建立超時索引
index_name = collection.create_index([("expiry", pymongo.ASCENDING)], expireAfterSeconds=0)

print(f"建立的超時索引名稱為: {index_name}")
```

這樣，MongoDB 將每分鐘檢查一次 "expiry" 欄位，並自動刪除過期的會話文檔。

請注意，expireAfterSeconds 參數的值應該設置為 0，這表示文檔將在 "expiry" 欄位中指定的時間過後立即過期。

通過這種方式，我們可以確保過期的會話文檔會自動被 MongoDB 刪除，從而保持數據庫的整潔。

## 補充說明⭐️

如果只有在 session_data 中新增 expiry 沒有創建超時索引 mongoDB 並不會清除過期的舊資料。這次遇到的問題就是 RD 有在每一筆資料中建立 expiry 但是並沒有建立 index 導致 mongoDB 沒辦法如預期清除舊資料，導致磁碟空間慢慢被佔用。

## 參考文獻📚

- [玩轉 Python 與 MongoDB_Day25_超時索引 TTL Index](https://ithelp.ithome.com.tw/m/articles/10327175)
