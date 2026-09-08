---
title: "Redis 不夠用？Redis Cluster 來幫你實現高可用與高吞吐量"
date: 2026-09-08T09:25:59+08:00
tags: ["Redis", "Redis Cluster"]
draft: false
description: ""
---

## 前言🔖

在軟體開發中，為了減輕資料庫的負擔，我們常常會採用快取資料庫的方式來提升系統的效能。我最常使用的快取資料庫是 Redis，它是一個高效能的鍵值資料庫，支援多種資料結構，如字串、哈希、列表、集合等。

Redis 會將資料存放在記憶體中，因此讀取速度非常快，也可以透過持久化機制將資料寫入磁碟，確保資料不會因為系統重啟而丟失。如果 Redis 在 Standalone 的模式下已經能優化你的系統效能，那麼什麼時候會需要使用 Redis Cluster 呢？

我認為有兩種情況會需要使用 Redis Cluster：

1. 應用程式對於 Redis 依賴度很高，你需要保證 Redis 的高可用性，避免單點故障導致整個系統不可用。
2. 大量的業務請求，併發量很高，單個 Redis 節點無法承受這麼大的壓力，需要透過分片的方式來分散負載。

## Redis Cluster 介紹📄

Redis Cluster 是一個分散式的 Redis 部署方案，它可以將資料分散存放在多個節點上，並且支援自動分片和故障轉移。這樣一來，即使某個節點發生故障，其他節點仍然可以繼續提供服務，保證系統的高可用性。

既然是分散式的部署方案，那麼 Redis Cluster 是如何將資料分散存放在多個節點上的呢？Redis Cluster 採用了一種叫做「哈希槽」的機制，英文稱為 Hash Slot。Redis Cluster 將所有的鍵值對映射到 16384 個哈希槽中，上限就是 16384 個哈希槽，每個叢集都一樣。

哈希槽只會分配給叢集中的 Master 節點，Slave 節點不會分配哈希槽。當我們新增一個 Master 節點時，需要從其他的 Master 節點中遷移一些哈希槽到新的 Master 節點上，這樣才能保證資料的均衡分佈。

如果我們將所有的哈希槽平均分配給 3 個 Master 節點，那麼每個 Master 節點就會分配到 16384 / 3 = 5461 個哈希槽。

```txt
# Redis叢集配置
                          client
                            |
                            V
--------------------------------------------------------------
       Redis               Redis               Redis
     (Master)            (Master)            (Master)
    |        |           |       |           |       |
    V        V           V       V           V       V
  Redis    Redis       Redis    Redis       Redis    Redis
(Replica) (Replica)  (Replica) (Replica)  (Replica) (Replica)
--------------------------------------------------------------
示意   1/3 Data            1/3 Data             1/3 Data
```

前面有提到 Cluster 架構除了可以提高吞吐量之外，還可以提高系統的可用性。那麼 Redis Cluster 是怎麼實現高可用性的呢?

這裡會提到兩個概念，分別是主從複製（Master-Slave Replication）和故障轉移（Failover）。

首先，Redis Cluster 中的每個 Master 節點都可以有多個 Slave 節點，Slave 節點會複製 Master 節點的資料。這個部分就是主從複製的概念，可以想像是資料的備份。

再來，我們會提到故障轉移的概念，例如：Master 節點 A 發生故障，這時候 Cluster 裡的 Master 節點 B 和 C 會發現 Master 節點 A 斷線了，此時候 Master 節點 B 和 C 會進行投票（2/3票超過半數），來判定 Master 節點 A 是否真的故障。

Slave 節點 A1、A2 會檢查自己與 Master 節點 A 的資料同步偏移量（Offset），確保資料是最新的，其中一個 Slave 節點會被選舉成為新的 Master 節點，並且將原本的 Master 節點 A 的哈希槽分配給新的 Master 節點，這樣就完成了故障轉移的過程。

## 參考文獻📚

- [Day27 Redis架構實戰-Redis叢集Slot分流機制](https://ithelp.ithome.com.tw/articles/10281010)
