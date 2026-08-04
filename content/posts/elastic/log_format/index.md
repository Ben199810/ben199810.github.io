---
title: "Log 設計 & 如何有效收集特定級別的 Log"
date: 2026-06-02T08:53:04+08:00
draft: false
description: "在這篇文章中，我們將介紹 log 設計的基本原則，以及如何有效的收集特定級別的 log，並且會介紹 ElasticSearch 在處理 log 的時候會有什麼限制。"
tags: ["ElasticSearch", "Log", "Log Design", "Log Collection"]
---

## 前言🔖

為什麼會需要設計 log 的格式？

不管是在開發過程或者是在運維的過程中，log 提供給開發者跟運維人員許多重要的資訊，可以從 log 中得知系統的狀態、有幾筆錯誤的異常資訊等...，既然 log 有助於我們排查錯誤，那麼設計良好的 log 格式就可以幫助我們更快的找到問題所在，甚至在 log 中就可以直接看出問題的原因。

## 設計原則🎯

log 設計的基本方針就是根據使用的目的來設計 log 的格式，以下會先介紹幾個基礎的 log 格式設計原則：

### 級別🎚

log 的等級可以幫助我們快速的判斷 log 的重要程度，常見的 log 等級有：

| 種類 | 說明 |
| :---: | :---: |
| FATAL | 發生致命錯誤的狀態 |
| ERROR | 發生錯誤的狀態 |
| WARN | 發生警告的狀態 |
| NOTICE | 正常但重要的狀態 |
| INFO | 系統資訊 |
| DEBUG | 有關於系統如何運作的訊息 |

為什麼會需要分這個多的等級？除了可以透過搜尋引擎快速的定位到重要的 log 以外，也可以幫助在不同的產品環境中調整要輸出的 log 等級，例如在開發環境中可能會輸出 DEBUG 等級的 log，而在生產環境中則只輸出 ERROR 等級的 log。

如果 log 是蒐集到 SaaS 平台上，例如 Datadog...，在特定的環境中只輸出特定等級的 log 也可以幫助我們節省成本，因為 SaaS 平台通常是按照 log 的容量來收費的。

#### 血淚史🥲

之前有同事在生產環境中為了要找生產環境的問題，將 log 輸出的級別調整為 TRACE，排查完問題以後忘記調整回來，導致生產環境中輸出大量的 log，在月底時 Datadog 的帳單金額暴增了幾萬美金。

![Datadog 帳單暴增](/img/posts/elastic/log_format/datadog_bill.png)

### 輸出的位置📂

log 的輸出位置需要開發人員與運維人員共同協商決定，如果是輸出 log 文件建議創建一個 logs 的資料夾來存放 log 文件，這樣可以幫助我們更好的管理 log 文件。

目前在內部常見的 log 輸出位置的資料夾路徑有兩個：

```shell
~/app/${app_name}/logs
~/app/${app_name}/log
```

建議使用第一個路徑，因為目前管理的服務內有些會同時輸出不同的 log 文件，例如 task.log、error.log...。

log 文件名稱的命名建議使用以下的格式：

```shell
default.log
```

不建議的命名格式：

```shell
${app_name}-${date}.log
```

在相同的設定條件`(*.log)`下，單一的變數名稱可以幫助 log agnet 在跟讀 file 時，花費較少的記憶體。

{{< mermaid >}}
graph LR
    log_agent(agent) -->|跟讀| log_file(default.log)
{{< /mermaid >}}

{{< mermaid >}}
graph LR
    log_agent(log agent) -->|跟讀| log_file1(app-2026-05-02.log)
    log_agent(log agent) -->|跟讀| log_file2(app-2026-05-02.01.log)
    log_agent(log agent) -->|跟讀| log_file3(app-2026-05-02.02.log)
{{< /mermaid >}}

#### 問題思考：log 文件如何進行 rotation？🔄

使用 logrotate 來進行 log 文件的 rotation，進行 rotation 後的 log 文件會重新命名成以下的結構：

```shell
logs/
├── default.log
├── default.log-2026-05-05
├── default.log-2026-05-04
├── default.log-2026-05-03
└── default.log-2026-05-02
```

這樣輪替以後的 log 文件名稱也不會被 log agent 繼續跟讀，因為 log agent 只會跟讀 default.log 這個文件。

### log 的格式📝

log 的格式建議使用 JSON 格式，因為 JSON 格式可以幫助我們更好的結構化 log 的內容，並且可以幫助我們更快的解析 log 的內容。

log 的格式或是內容通常會因為不同的產品或是服務而有所不同，以下是一個常見的 log 格式範例：

```json
{
  "level": "error", string
  "timestamp": "2026-06-02T08:53:04+08:00", datetime
  "method": "GET", string
  "path": "/api/v1/users", string
  "full_url": "http://example.com/api/v1/users", string
  "status_code": 500, integer
  "latency_seconds": 0.025, float
  "msg": "Internal Server Error", string
  "request": {}, object
  "response": {}, object
  "game_id": "01" string
}
```

注意：大小寫的問題，建議使用小寫的 key，這樣在使用 log agent 解析 log 的時候可以避免大小寫不一致的問題。

#### 問題思考：log 應該要包含哪些欄位？🤔

輸出上我們可以依據 5W1H 的原則來設計，並且加上必要的資訊，不應該過多或不足。

1. When --> 何時執行該程序
2. Who --> 是誰執行該程序
3. Where --> 該程序在哪裡執行
4. What --> 該程序執行了什麼
5. Why --> 為什麼執行該程序

## ElasticSearch 有什麼 log 的限制？⚠️

ElasticSearch 在處理 log 的時候，會有一些限制需要注意：

1. index 中 log 欄位的型別突然轉換了，例如之前是 string 的欄位突然變成 integer，這樣就會導致 ElasticSearch 拒絕接受新的 log，因為 ElasticSearch 會認為這是一個 mapping 的錯誤。
2. index 中 log 欄位數量上限，ElasticSearch 預設的 index 中 log 欄位數量上限是 1000。

## agent 如何收集特定級別的 log？🤔

1. 開發人員定義好 log 文件的分類，例如 default.log、error.log、debug.log，開發人員透過設定決定輸出哪些級別的 log 到特定的 log 文件中，再由 log agent 來跟讀特定的 log 文件，這樣就可以達到收集特定級別的 log 的目的。
{{< mermaid >}}
graph LR
    app_config(app config) -->|設定| app(app)
    app(app) -->|輸出| log_file1(default.log)
    app(app) -->|輸出| log_file2(error.log)
    log_agent(log agent) -->|跟讀| log_file1(default.log)
    log_agent(log agent) -->|跟讀| log_file2(error.log)
    log_agent(log agent) -->|跟讀| log_file3(debug.log)
{{< /mermaid >}}

2. 開發人員將 log 輸出到同一個 log 文件中，例如 default.log，運維人員透過 log agent 的設定來過濾特定級別的 log，例如只收集 error 級別的 log，這樣就可以達到收集特定級別的 log 的目的。
{{< mermaid >}}
graph LR
    app_config(app config) -->|設定| app(app)
    app(app) -->|輸出| log_file(default.log)
    log_agent(log agent) -->|跟讀| log_file(default.log)
    log_agent(log agent) -->|level: error| es(elastic search)
{{< /mermaid >}}

## 參考文獻

- [Day28 - 事到如今問不出口的 Log 基礎和設計指南](https://ithelp.ithome.com.tw/articles/10338905)
