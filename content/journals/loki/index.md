---
title: "Loki"
date: 2026-03-30T12:56:16+08:00
draft: true
description: ""
---
## 前言🔖

近期在幫公司尋找能夠平替 Elasticsearch 的日誌系統，這段期間研究了 Loki，雖然最後在實務上沒有採用。但還是想把這段期間的研究心得記錄下來，分享給有興趣的朋友。

## Loki 是什麼？🤔

首先來簡單的介紹今天的主角：Loki。Loki 是由 Grafana Labs 開發的一款分散式日誌系統，專為大規模日誌收集和查詢而設計。它的核心理念是「索引少，存儲多」，與傳統的 Elasticsearch 不同，Loki 只對日誌的元數據（如標籤）進行索引，而不對日誌內容進行全文索引。這使得 Loki 在處理大量日誌時具有更高的效率和更低的成本。

## Loki 的架構🧱

Loki 的架構主要由以下幾個組件組成：

1. **Distributor**：負責接收來自客戶端的日誌數據，並將其分發到後端的 Ingester。
2. **Ingester**：負責接收來自 Distributor 的日誌數據，並將其寫入存儲後端。
3. **Querier**：負責處理來自客戶端的查詢請求，從 Ingester 中檢索日誌數據並返回結果。
4. **Storage**：Loki 支持多種存儲後端，例如本地文件系統、Amazon S3、Google Cloud Storage 等，用於存儲日誌數據。

題外話，當時在研究 Loki 的架構時，因為發現他可以使用 Google Cloud Storage 作為存儲後端，比起 Elasticsearch 的磁碟存儲，可以省下不少成本。

## 實作練習🛠️
