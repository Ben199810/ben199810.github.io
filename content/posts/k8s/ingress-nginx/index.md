---
title: "Ingress Nginx Controller"
date: 2023-08-19
draft: false
description: ""
tags: ["kubernetes", "ingress"]
---
隨著系統架構日益複雜，可能需要使用多個 Ingress 來分離不同服務的流量管理。這樣做的好處是當某個 Ingress 發生異常時，不會影響到所有服務的運作。

不過缺點是每個 Ingress 都需要使用靜態 IP，在 GCP 等雲端服務中，每個保留的靜態 IP 都會增加成本。

我們可以使用 Ingress Controller 來統一管理所有的 Ingress 資源，只使用一個或少數幾個靜態 IP，這樣可以降低成本並簡化管理。

上一篇文章中有提到 ingress，如果想瞭解 ingress 可以先參考或預習這篇文章。

{{< article link="/posts/k8s/ingress/" >}}

## Ingress Nginx Controller

Ingress Nginx Controller 結合了 Ingress 的簡潔並支援 Nginx 相關的擴充功能，讓我們能更好的管理所有的 ingress。

## Nginx

- 高效能的 webServer 遠勝傳統 apache server 的資源與效能
- 大量的模組與擴充功能
- 充足的安全性功能
- 輕量
- 容易水平擴展

## Ingress

- Service 連接
- LoadBalance 設定
- SSL/TLS 終端
- 虛擬主機設定

## 安裝

```bash
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace
```

## 實際範例

### 基本 Ingress 設定

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: example-service
            port:
              number: 80
```

### 進階設定範例

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: advanced-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "10"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - secure.example.com
    secretName: example-tls
  rules:
  - host: secure.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
```

<div style="background-color:white; padding: 20px">
{{< mermaid >}}
graph LR
  
  ingress1(Ingress-1)
  ingress2(Ingress-2)
  ingress3(Ingress-3)

  subgraph Ingress Nginx Controller
    controller(Controller)
    admission(Admission Webhook)
    nginx(Nginx)

    controller -->|配置| nginx
    controller -->|驗證| admission
  end

  ingress1 -->|管理| controller
  ingress2 -->|管理| controller
  ingress3 -->|管理| controller
{{< /mermaid >}}
</div>

## 參考資料

[使用 Helm 來安裝 Ingress Controller](https://kubernetes.github.io/ingress-nginx/deploy/#quick-start)

[ingress-nginx](https://github.com/kubernetes/ingress-nginx)
