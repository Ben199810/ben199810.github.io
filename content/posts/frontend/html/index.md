---
title: "HTML 基礎學習筆記"
date: 2026-08-11T10:28:52+08:00
draft: true
tags: ["HTML", "Note"]
description: "個人學習 HTML 的筆記，目前不是很完整，僅供自己複習使用。"
---

## 簡介

html 是一個超文本標記語言，主要是告訴瀏覽器會需要顯示哪些內容，可以是文字、圖片、連結等。

它就像是 markdown 語法一樣，用來記錄文本的語言。

html 主要可以分成三個部分:

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

## 參考文獻

- [HTML 語法教學，HTML 入門新手必學](https://tw.alphacamp.co/blog/html-guide)
