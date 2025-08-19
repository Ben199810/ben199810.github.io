---
title: "Rewrite vs Redirect"
date: 2025-08-19T08:47:58+08:00
draft: false
tags: ["nginx", "rewrite", "redirect"]
description: "nginx 的 rewrite 和 redirect 的差異"
---
## 前言

近期公司網站要下架舊的前端網頁服務，ingress 調整後端服務路由。

新的服務網頁使用 nginx `rewrite` 網址路徑。在檢查過程中發現在瀏覽器頁面會發現有些前端靜態資源渲染不出來，呈現空白的頁面。

後來使用 `redirect` 方式，問題解決了。

所以想要記錄一下 `rewrite` 和 `redirect` 的差異。

## rewrite

nginx 的 rewrite 是一種用於修改請求 URL 的規則機制，常用於 URL 重寫、導向（redirect）、隱藏真實路徑或做 SEO 優化。

### 基本語法

- regex: 正則表達式，用於匹配原始的請求路徑。
- replacement: 要替換成的新路徑或新的 URL。
- flag: 可選的標誌，控制 rewrite 行為的標誌，例如 permanent（301）、redirect（302）、break、last 等。

```nginx
rewrite regex replacement [flag];
```

### 參數

- last: 停止 rewrite，將請求重新在 server 或 location 區塊中尋找匹配（一般用於 location 區塊內）。
- break: 停止 rewrite，但不再重新尋找匹配，直接執行後續配置。
- redirect: 臨時重定向（302），告知瀏覽器請求新的 URL。
- permanent: 永久重定向（301）。

`last` 跟 `break` 屬於內部重定向，不會改變瀏覽器的 URL。

當用戶訪問 `/old/path` 時，將其重寫為 `/new/path`。

```nginx
location / {
  rewrite ^/old/(.*)$ /new/$1 last;
}
```

`redirect` 跟 `permanent` 屬於外部重定向，會改變瀏覽器的 URL。

當用戶訪問 `/old/path` 時，將其重定向到 `/new/path`。

```nginx
location / {
  rewrite ^/old/(.*)$ /new/$1 redirect;
}
```

## 問題反思

在使用 `rewrite` 的過程中，發現某些靜態資源無法正確加載，這可能是因為 `rewrite` 會在內部處理請求，而不會改變瀏覽器的 URL，導致某些資源的請求路徑不正確。相對而言，`redirect` 會直接告訴瀏覽器新的請求路徑，從而避免了這個問題。

## 參考

[什麼是 Nginx rewrite？轉址的機制，與 return 301 或 redirect 的差別在哪？](https://blog.yuyansoftware.com.tw/2024/01/nginx-rewrite-return-301/)
