---
title: "Cert Manager in Kubernetes"
date: 2025-09-16T18:13:07+08:00
draft: false
description: ""
---
## 前言

之前有稍微了解過 cert-manager，最近公司服務壞掉了需要修好它，順便就來寫一篇文章紀錄一下

## 什麼是 cert-manager？

cert-manager 是一個 Kubernetes 的原生資源管理工具，主要用來自動化管理和發放 TLS/SSL 憑證。它可以與多種憑證頒發機構（CA）集成，如 Let's Encrypt、HashiCorp Vault 等，並且能夠自動續期憑證，確保應用程序的安全通信。

## 主要功能

1. cert-manager 會透過設定 cluster-issuer、issuer 來決定要使用哪一個 CA 來發放憑證，還有要管理的域名及驗證的方式。

    cluster-issuer 的作用範圍是整個 Kubernetes 叢集，而 issuer 的作用範圍則是單一命名空間。

2. Certificate 是 cert-manager 的核心資源，用來定義需要管理的憑證。它會指定要使用的 issuer、域名、密鑰等資訊。

3. 設定完成之後，cert-manager 會自動向指定的 CA 發出憑證請求，並將獲取的憑證存儲在 Kubernetes 的 Secret 中。在憑證即將過期時，cert-manager 會自動續期，確保始終擁有有效的憑證。

## 流程圖

<div style="background-color:white; padding: 20px">
{{< mermaid >}}
flowchart
  manager[cert-manager] --> certificaterequest[Certificate Request] --> issuer[Issuer/ClusterIssuer]
  issuer --> ca[Let's Encrypt/HashiCorp Vault]
  ca --> certificate[Certificate]
  certificate --> secret[Secret]
  secret --> ingress[Ingress/Service]
{{< /mermaid >}}
</div>

## 遇到的問題

透過網址訪問 API 服務時出現 `SSL certificate problem: certificate has expired` 的錯誤訊息，表示憑證已經過期了。那為什麼 cert-manager 沒有自動續期呢？發生了什麼錯誤就是我們要去調查的重點。

1. 首先從流程圖可以知道，cert-manager 要更新 certificate 的時候會先建立一個 Certificate Request，可以從 describe 觀察到 event 顯示 Referenced ClusterIssuer not found，表示找不到對應的 ClusterIssuer。

    ![cert-manager event](/img/k8s/cert-manager/certificate-request-event.png)

2. 接著我們去查看 ClusterIssuer，可以發現 "letsencrypt" 這個 ClusterIssuer 根本不存在。

    圖的話忘記截了，總之就是找不到這個 ClusterIssuer。🤣

    因為 helm release 的 values 設定裡是存在的，所以使用 apply 也不會再建立一次。所以用 `helmfile sync` 重新部署一次。

    完成之後，certificate request 就可以成功透過 ClusterIssuer 來向 Let's Encrypt 申請憑證了。

## 參考文章

- [使用 cert-manager 管理 K8S TLS 憑證](https://medium.com/starbugs/%E4%BD%BF%E7%94%A8-cert-manager-%E7%AE%A1%E7%90%86-k8s-tls-%E6%86%91%E8%AD%89-ab6258af9195)
