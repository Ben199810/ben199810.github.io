---
title: "前端基礎學習筆記"
date: 2026-08-11T10:28:52+08:00
draft: true
tags: ["Frontend", "Note"]
description: "個人學習前端的筆記，目前不是很完整，僅供自己複習使用。"
---

## HTML

HTML 是一個超文本標記語言，主要是告訴瀏覽器會需要顯示哪些內容，可以是文字、圖片、連結等。

它就像是 Markdown 語法一樣，用來記錄文本的語言。

HTML 主要可以分成三個部分:

1. 宣告
2. 標頭
3. 主體

### 宣告

按照流程宣告是第一個需要先做的事情！

`<!DOCTYPE html>` 告訴瀏覽器這是一份 HTML5 的網頁，瀏覽器用正確的方式去展示網頁內容。

接著，開始開始撰寫 HTML 文件，開頭需要使用 `<html>` 標籤，結尾使用 `</html>` 標籤。內容會放入標頭跟主體！

```html
<!-- 宣告 HTML5 文件類型 -->
<!DOCTYPE html>
<!-- 完整的 HTML 文件，會包含標頭與主體 -->
<html>
  <head>
    ...
  </head>
  <body>
    ...
  </body>
</html>
```

### 標頭

標頭是要告訴瀏覽器的資訊，不會顯示給使用者知道。例如: google 搜尋引擎。

例如下面的範例:

meta 是代表網頁資訊描述標籤，它告訴了瀏覽器內容是 HTML，並且使用 UTF-8 編碼。

⭐️ UTF-8 是一種編碼方式，能夠支援多國語言，像是中文、英文、日文等。

```html
<head>
  <!-- 文件類型 content="text/html; charset=utf-8" -->
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
```

### 主體

最後就是主體了，主體是要告訴瀏覽器要顯示的內容，像是文字、圖片、連結等。跟使用者互動的部分都會放在主體裡面。可以想像你開始撰寫網頁內容，就像是寫一篇文章一樣，會有標題、段落、圖片、連結等。

```html
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>範例網頁</title>
  </head>
  <body>
    <h1>這是主體內容</h1>
    <p>這是一個段落。</p>
  </body>
</html>
```

隨著學習的深入，會慢慢了解到更多的 HTML 標籤，像是圖片、連結、表格、表單等:

- 標題: `<h1>`、`<h2>`、`<h3>`、`<h4>`、`<h5>`、`<h6>`
- 段落: `<p>`
- 連結: `<a>`
- 強調: `<strong>`、`<em>`，strong 是加粗，em 是斜體。
- 清單: `<ul>`、`<ol>`、`<li>`，ul 是無序清單，ol 是有序清單，li 是清單項目。
- 圖片: `<img>`
- 表格: `<table>`、`<tr>`、`<td>`、`<th>`
- 表單: `<form>`、`<input>`、`label`
- 區域: `<div>`、`<span>`
- 換行: `<br>`，br 是換行標籤，沒有結尾標籤。
- 水平線: `<hr>`，hr 是水平線標籤，沒有結尾標籤。

### 延伸學習

導覽列，在網頁的頁首，通常會放置網站的主要連結，方便使用者快速瀏覽網站的不同頁面。

```html
<nav className="navbar">
  <div className="nav-container">
    <div className="logo">FlyRide 機場接送</div>
    <ul className="nav-menu">
      <li><a href="#home" className="active">首頁</a></li>
      <li><a href="#vehicles">車款介紹</a></li>
      <li><a href="#pricing">接送價格</a></li>
      <li><a href="#contact">聯絡方式</a></li>
    </ul>
  </div>
</nav>
```

## CSS

CSS 是一種樣式表語言，用來描述 HTML 文件的外觀和格式。它可以控制網頁的顏色、字體、排版、佈局等，使網頁更美觀和易於閱讀。

可以看到 CSS 宣告了 h1 標籤的字體應該要是 32px，並且置中對齊。過程中會使用屬性 (property) 與屬性值 (value) 來描述樣式。

```html
<h1>我是一個 h1 且字體大小是 32px 的置中標題</h1>

h1 { font-size: 32px; text-align: center; }
```

建議可以將 CSS 獨立管理在 style.css 檔案中，並且在 HTML 文件中使用 `<link>` 標籤引入。

```html
<link rel="stylesheet" href="style.css" />
```

<!-- prettier-ignore -->
{{< mermaid >}}
graph LR
  A[HTML] -->|uses| B[CSS]
{{< /mermaid >}}

## 參考文獻

- [前端工程師全攻略：必備技能樹與職涯階段](https://tw.alphacamp.co/blog/frontend-developer)
