---
title: "sticky session in kubernetes"
date: 2025-08-24T16:27:00+08:00
draft: false
tags: ["kubernetes", "session", "sticky session"]
description: ""
---
## 前言

近期公司有 socket.io 的服務需要可以擴展，由於是聊天室服務，有實時的雙向通信需求（如聊天室、遊戲、實時協作工具）。保持用戶端保持與同一服務器的連接可以：

- 確保消息順序一致性
- 減少連接重建的開銷
- 維護實時狀態同步

## 實作

1. 建立 backendConfig 設定 sessionAffinity。

  ```yaml
  apiVersion: cloud.google.com/v1
  kind: BackendConfig
  metadata:
    name: socket-backendconfig
  spec:
    sessionAffinity:
      affinityType: "GENERATED_COOKIE" # Options: NONE, CLIENT_IP, GENERATED_COOKIE
      affinityCookieTtlSec: 50
  ```

2. 在 kubernetes 的 serivce 中，要先設定 network endpoint group (NEG)，設定的方式有兩種：

   - 獨立創建 NEG，不管有沒有套用 google load balancer 都會創建一個 NEG。

   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: socket-service
     annotations:
       cloud.google.com/neg: '{"exposed_ports": {"80":{"name": "NEG_NAME"}}}'
       cloud.google.com/backend-config: '{"default": "socket-backendconfig"}'
   spec:
     selector:
       app: socket-app
     ports:
       - protocol: TCP
         port: 80
         targetPort: 3000
     type: ClusterIP
     sessionAffinity: ClientIP
   ```

   - 依賴於 google load balancer 的自動創建 NEG。

   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: socket-service
     annotations:
       cloud.google.com/neg: '{"exposed_ports": {"80":{"name": "NEG_NAME"}}}'
       cloud.google.com/backend-config: '{"default": "socket-backendconfig"}'
   spec:
     selector:
       app: socket-app
     ports:
       - protocol: TCP
         port: 80
         targetPort: 3000
     type: ClusterIP
     sessionAffinity: ClientIP
   ```

3. 建立 ingress

  這邊要特別注意的是，這次實作使用的是 GCP 的 NEG，也是要搭配 GCP 的 load balancer 使用。才能達到這次實作的需求。

  因為有使用自己在 github 開源專案建立的 [ingress-nginx](https://github.com/kubernetes/ingress-nginx)，進行串接。但是在前端檢查的時候，發現沒有 GCLB 這個 cookie。

  ```yaml
  apiVersion: networking.k8s.io/v1
  kind: Ingress
  metadata:
    name: socket-ingress
    annotations:
      kubernetes.io/ingress.class: "gce"
  spec:
    rules:
      - host: socket.example.com
        http:
          paths:
            - path: /
              pathType: Prefix
              backend:
                service:
                  name: socket-service
                  port:
                    number: 80
  ```

  都建立完成以後，可以透過以下方式進行測試

  ```bash
  curl -i -X GET http://socket.example.com
  ```

## 問題反思

這次的實作過程中，雖然這種方式看似可以保持客戶端與同一伺服器的連結。但因為是聊天室服務，可能還是會有一些問題需要注意：

⭐️ session 親和性只是盡可能保持連接在同一伺服器，但無法保證 100% 的穩定性。如果第一次連線是連到 A 伺服器，之後因為某些原因（如伺服器重啟、負載均衡策略變更等）可能會被導向 B 伺服器，這樣就會導致用戶體驗不一致。

下面是跟一位同仁討論之後紀錄下來的簡易架構圖：

- client 端在一開始連線的時候，就是不同的 socket_server
- client 端同時也會透過 api 對 MQ 或者 Pub/Sub 進行訊息的發送。
- server 端可以依據 `channel` 進行訊息的路由。同步給在不同 socket_server 的 client。

<div style="background-color:white; padding: 20px">
{{< mermaid >}}
flowchart

client01
client02
MQ/Pub_Sub
socket_server01
socket_server02

client01 --channel,msg--> MQ/Pub_Sub
client02 --channel,msg--> MQ/Pub_Sub
MQ/Pub_Sub --> socket_server01
MQ/Pub_Sub --> socket_server02

socket_server01 <--> client01
socket_server02 <--> client02

{{< /mermaid >}}
</div>

## 參考資料

- [在 GCP/GKE 的 Ingress 設定 sticky session](https://aaronjen.github.io/2020-09-11-gke-ingress-sticky-session/)
- [透過獨立的區域 NEG 使用容器原生負載平衡](https://cloud.google.com/kubernetes-engine/docs/how-to/standalone-neg?hl=zh-tw)
- [同事的腦袋 🧠](https://blog.cosparks.app)
