---
title: "Elastic Data Streams 自動化管理 Index 的生命週期"
date: 2026-01-21T11:45:37+08:00
draft: false
tags: ["Elastic", "Data Streams"]
description: ""
---

## 前言🔖

Elastic是開發過程中常常幫助收集系統日誌(log)並且分析根本錯誤原因的好用工具之一，大量的日誌存放與管理，考驗運為團隊的經驗以及能力，Elastic其實能夠使用資料流(data streams)管理龐大的索引(index)資訊，減少運維團隊的負擔。

## Data Streams📃

Data Streams是 Elastic中的一個功能，主要用於處理時間序列資料，如日誌、指標等。它允許我們將資料自動分割成多個 索引，並根據設定的生命週期策略自動管理這些索引的刪除和轉換。

Data Streams可以拆分成兩個部分來看，分別是政策(policy)與模板(template)。這兩個重要的部分，是組成資料流重要的核心。

## Policy📌

### Index Lifecycle Policy

第一步，我們需要建立一個索引生命週期(index lifecycle management)，以下是一個索引生命週期的範例:

在熱(hot)資料處理階段，設定了幾個 actions，其中 rollover的主要功能是索引達到特定的條件，會自動建立一個新的索引存放新寫入的資料。

範例中設定了兩個條件一個是索引資料大小超過 50gb，一個是索引超過 7天，只要到達其中一個條件，就會建立一個新的索引。

在暖(warm)資料處理階段，主要是將資料收攏釋出硬碟的存儲空間。forcemerge的功能是減少索引底層的段(segment)數量，`"max_num_segments": 1` 代表將該索引內所有的段，強行合併成 1個單一的段。shrink主要是減少索引的分片數量，可以降低叢集管理大量分片的負擔。

⭐️ 補充: 為什麼會使用 forcemerge而不是 merge，因為在 elastic中，當刪除或更新文件時，資料並不會立刻從硬碟上消失，而是會被標記為「已刪除」。只有執行 forcemerge，系統才會真正把這些被刪除的資料從硬碟刪除，釋放磁碟空間。

最後，刪除(delete)資料處理階段，會刪除叢集裡的快照索引，負責把之前建立的快照和索引徹底刪除。

```json
PUT _ilm/policy/my-lifecycle-policy
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_age": "7d",
            "max_primary_shard_size": "50gb"
          }
        }
      },
      "warm": {
        "min_age": "2d",
        "actions": {
          "forcemerge": {
            "max_num_segments": 1
          },
          "shrink": {
            "number_of_shards": 1
          }
        }
      },
      "delete": {
        "min_age": "7d",
        "actions": {
          "delete": {
            "delete_searchable_snapshot": true
          }
        }
      }
    }
  }
}
```

如果有建立可以訪問 Elastic 的網址，可以透過網址來執行的 API 語法新增政策，例如：

```bash
curl -X PUT "https://your-api-domain/_ilm/policy/my-lifecycle-policy" \
-H 'Content-Type: application/json' \
-d'
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_age": "7d",
            "max_primary_shard_size": "50gb"
          }
        }
      },
      "warm": {
        "min_age": "2d",
        "actions": {
          "forcemerge": {
            "max_num_segments": 1
          },
          "shrink": {
            "number_of_shards": 1
          }
        }
      },
      "delete": {
        "min_age": "7d",
        "actions": {
          "delete": {
            "delete_searchable_snapshot": true
          }
        }
      }
    }
  }
}'
```

新增完政策以後，代表我們已經規劃好資料流了，當然我們可以訂定很多不同的政策，例如: 保留 15 天或保留 10 天的政策。接著我們需要將定義好的政策套用在索引上。

## Template📌

在 Elasticsearch 中，模板的核心目的是「定義自動化的規格」。當系統有新資料寫入、需要建立新索引時，它會自動檢查有沒有匹配的模板。如果有，就會依照模板規定的設定(settings)和欄位格式(mappings)把索引建立出來，不需要每次手動設定。

模板分成了兩個層級，元件模板(component template)與索引模板(index template)，我們可以想像兩個模板之間的關係就像是積木與樂高的概念。

### Component Template

一句話定義：它是「局部、可重複使用的配置片段」，就像是樂高積木，或者程式碼中的 Class(類別) / Module(模組)。它本身不能直接拿來建立索引，它是被設計來給別人「組合」用的。

常見的應用是把通用的配置獨立成不同的元件模板，例如:

- component_setting_standard: 專門定義通用的基礎設定(如 Shard 數量、Replica 數量、ILM Policy 綁定)
- component_mapping_k8s: 專門定義 K8s日誌專用的欄位格式(如 pod_name, namespace)
- component_mapping_security: 專門定義資安稽核專用的欄位格式(如 src_ip, dst_ip)

```json
PUT _component_template/my-logs-settings
{
  "template": {
    "settings": {
      "index.lifecycle.name": "my-lifecycle-policy", // 指定 ILM 策略，自動管理滾動與刪除
      "index.codec": "best_compression"
    }
  }
}

PUT _component_template/my-logs-mappings
{
  "template": {
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" }, // Data Stream 必須包含 @timestamp 欄位
        "message": { "type": "text" }
      }
    }
  }
}
```

### Index Template

接著，我們需要建立一個 Index Template，來將 Component Template 套用到 Data Stream 上。以下是一個範例：

```json
PUT _index_template/my-logs-template
{
  "index_patterns": ["logs-my-app-*"], // 匹配此模式的寫入將自動轉為 Data Stream
  "data_stream": {},                  // 啟動 Data Stream 功能
  "composed_of": [ "my-logs-settings", "my-logs-mappings" ], // 組合上面的組件
  "priority": 500
}
```

建立完成後，可以開啟 Kibana 的 Management 頁面，確認 Index Template 是否正確建立。如下圖所示：

![Index Template 範例](/img/elastic/data-streams/template_example.png "Index Template 範例")

### 補充說明⭐️

Index Template 使用 composed_of 屬性來組合多個 Component Template，也可以將設定直接寫在 Index Template 裡面。選擇不創建 Component Template 也是可以的。

## 測試 Data Stream🚀

當以上的準備工作都完成後，我們就可以開始測試 Data Stream 了。使用任何的 Log Agent 工具（如 Filebeat、Fluentd 等）將日誌資料寫入符合 Index Template 模式的 Index 名稱，例如 logs-my-app-000001。Elastic 會自動將其轉換為 Data Stream，並根據我們設定的 ILM 策略來管理 Index 的生命週期。

下圖是從 Server 收集到的日誌資料，並成功寫入 Data Stream：

![Data Stream 日誌寫入範例](/img/elastic/data-streams/logs_index.png "Data Stream 日誌寫入範例")

### 補充說明⭐️

透過 Data Streams 管理的 Index，會加上 `.ds-` 前綴來區分一般的 Index。例如，logs-my-app-000001 會變成 .ds-logs-my-app-000001。在 Kibana 頁面上要打開 Include hidden indices 才能看到這些 Index。

## 結語📝

透過 Elastic 的 Data Streams 功能，我們可以輕鬆地自動化管理 Index 的生命週期，減少手動維護的工作量，並提高系統的穩定性和彈性。希望這篇文章能幫助大家更好地理解和使用 Data Streams 來管理日誌資料。

## 參考文獻📚

- [Elastic 官方文件 - Data Streams](https://www.elastic.co/docs/manage-data/data-store/data-streams)
- [Elastic 官方文件 - Set up a data stream](https://www.elastic.co/docs/manage-data/data-store/data-streams/set-up-data-stream)
