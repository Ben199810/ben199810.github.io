---
title: "Kubernetes Job"
date: 2025-08-13T09:28:49+08:00
draft: false
tags: ["kubernetes", "job"]
description: ""
---
## 介紹

Job 表示一次性的任務，執行完成後就會停止。

Job 可以建立一個或多個 Pod，並將繼續重試 Pod 的執行，直到指定數量的 Pod 成功終止。

## 範例

在系統中部署新的服務時，可以使用 Job 透過 command line 工具或腳本來執行一次性的任務，例如資料庫遷移、批次處理等。

- backoffLimit
  - 指定 Pod 失敗後重試的次數。如果重試次數超過此限制，Job 將被標記為失敗。
- restartPolicy
  - Pod 的容器可能因為多種不同的原因失效，"OnFailure" 使 Pod 留在目前的節點上，但容器會重新運行。
  - "Never"，當 Pod 失敗時，Job 控制器會啟動新的 Pod。
  - 只能使用 "Never" 或 "OnFailure"。
- activeDeadlineSeconds
  - 指定 Job 的最大執行時間（以秒為單位）。如果 Job 在此時間內未完成，則會被終止。
  - activeDeadlineSeconds 的優先權高於 backoffLimit。
- ttlSecondsAfterFinished
  - Job 完成後預設是不會被清理的，可以設定此參數來指定 Job 完成後保留的時間（以秒為單位）。當時間到達後，Job 將被自動清理。

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: example-job
spec:
  ttlSecondsAfterFinished: 60
  activeDeadlineSeconds: 30
  template:
    spec:
      containers:
      - name: example
        image: example-image
        command: ["sh", "-c", "echo Hello, Kubernetes! && sleep 30"]
      restartPolicy: Never
  backoffLimit: 4
```
