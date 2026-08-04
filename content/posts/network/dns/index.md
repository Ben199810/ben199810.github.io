---
title: "DNS(Domain Name System)"
date: 2026-07-22T11:00:55+08:00
draft: false
description: ""
---

## 簡介

DNS（Domain Name System）是一種將域名轉換為 IP 位址的系統。它是互聯網的基礎設施之一，允許用戶通過易於記憶的域名訪問網站，而不需要記住複雜的數字 IP 位址。

## DNS 的工作原理

載入網頁會涉及 4 個 DNS 伺服器:

- DNS Resolver（遞迴解析器）: 接收來自用戶端機器的查詢
- Root Name Server（根名稱伺服器）: 將可讀的主機名稱轉譯（解析）為 IP 位址的第一個步驟
- TLD Name Server（頂級域名伺服器）: 搜尋特定 IP 位址的下一步，其代管主機名稱的最後一部分（例如，在 example.com 中，TLD 伺服器為「com」）
- Authoritative Name Server（權威名稱伺服器）: 如果權威名稱伺服器能夠存取請求的記錄，則其會將已請求主機名稱的 IP 位址傳回到發出初始請求的 DNS 解析程式

{{< mermaid >}}
flowchart LR
A[DNS Resolver] --> B[Root Name Server]
B --> C[TLD Name Server]
C --> D[Authoritative Name Server]
{{< /mermaid >}}

如果查詢對象為子網域（例如 foo.example.com 或 blog.cloudflare.com）的情況下，將向權威名稱伺服器之後的序列新增一個附加名稱伺服器，其負責儲存該子網域的 CNAME 記錄。

{{< mermaid >}}
flowchart LR
A[DNS Resolver] --> B[Root Name Server]
B --> C[TLD Name Server]
C --> D[Authoritative Name Server]
D --> E[blog.cloudflare.com Authoritative Name Server]
{{< /mermaid >}}

### DNS 查閱步驟

1. 使用者在 Web 瀏覽器中鍵入「example.com」，查詢傳輸到網際網路中，然後 DNS 遞迴解析程式接收該查詢。
2. 接著該解析程式查詢 DNS 根名稱伺服器 (.)。
3. 然後根伺服器使用儲存其網域資訊的頂層網域 (TLD) DNS 伺服器（例如 .com 或 .net）的位址回應該解析程式。搜尋 example.com 時，我們的請求會指向 .com TLD。
4. 然後該解析程式向 .com TLD 發出請求。
5. TLD 伺服器隨後使用該網域的名稱伺服器 example.com 的 IP 位址進行回應。
6. 最後，遞迴解析程式將查詢傳送到該網域的名稱伺服器。
7. 接著 example.com 的 IP 位址從名稱伺服器傳回該解析程式。
8. 然後 DNS 解析程式使用最初請求的網域的 IP 位址回應 Web 瀏覽器。

DNS 查閱的這 8 個步驟傳回了 example.com 的 IP 位址後，瀏覽器便能夠發出對該網頁的請求：

9. 瀏覽器向該 IP 位址發出 HTTP 請求。
10. 位於該 IP 的伺服器傳回將在瀏覽器中轉譯的網頁 (第 10 步)。

{{< mermaid >}}
flowchart LR
A[example.com] -->|1| B[DNS Resolver]
B -->|2| C[Root Name Server]
C -->|3| B
B -->|4| E[TLD Name Server]
E -->|5| B
B -->|6| F[example.com]
F -->|7| B
B -->|8| A

A -->|9| G[Server]
G -->|10| A
{{< /mermaid >}}

### 紀錄

DNS 常見的紀錄類型包括:

| 紀錄類型 | 說明                                          |
| -------- | --------------------------------------------- |
| A        | 將域名映射到 IPv4 位址                        |
| AAAA     | 將域名映射到 IPv6 位址                        |
| CNAME    | 將一個域名別名映射到另一個域名                |
| TXT      | 用於存儲任意文本資訊，常用於 SPF、DKIM 等驗證 |

## 參考文獻

- [什麼是 DNS？ | DNS 的工作方式](https://www.cloudflare.com/zh-tw/learning/dns/what-is-dns/)
