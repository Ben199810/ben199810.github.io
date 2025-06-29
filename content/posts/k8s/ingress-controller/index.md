---
title: "Ingress Controller 簡介"
date: 2023-08-19
draft: false
description: "k8s ingress controller 簡單介紹與安裝"
tags: ["k8s", "ingress"]

---
## 前言
隨著系統架構可能日益龐大，可能會使用複數的 ingress 來做進入服務的區分。以防止在 ingress 異常的時候，會影響全體的服務使用。缺點是複數的 ingress 需要使用靜態 IP。在 GCP 的服務上，每保留一組靜態 IP 服務就是增加成本。接著會介紹 ingress controller 這項服務用於管理所有的 ingress。

上一篇文章中有提到 ingress，如果想瞭解 ingress 可以先參考或預習這篇文章。
{{< article link="/posts/k8s/ingress/" >}} 

## Nginx Ingress Controller
這篇文章要講解的 Nginx Ingress Controller 結合了 Ingress 的簡潔並支援 Nginx 相關的擴充功能，讓我們能更好的管理所有的 ingress，下面會簡單提到 nginx 以及 ingress 優點。

### Nginx 介紹
nginx 是一款高效能、耐用、且功能強大的 loadBalance 及 webServer。也擁有很高的市佔率。
- 高效能的 webServer 遠勝傳統 apache server 的資源與效能
- 大量的模組與擴充功能
- 充足的安全性功能
- 輕量
- 容易水平擴展

### Ingress 介紹
定義外部到內部的設定。
- Service 連接
- LoadBalance 設定
- SSL/TLS 終端
- 虛擬主機設定

### 安裝
[使用 Helm 來安裝 Ingress Controller](https://kubernetes.github.io/ingress-nginx/deploy/#quick-start)

```bash
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace
```

#### values
使用 Helm 進行安裝，需要做調整，並想要參考有哪些值是可提供使用者調整。可以使用下列的指令輸出 values.yaml。

或者到 [Github](https://github.com/kubernetes/ingress-nginx) 上閱讀整個服務的是如何運作跟建立的

```bash
helm show values ingress-nginx --repo https://kubernetes.github.io/ingress-nginx
```
