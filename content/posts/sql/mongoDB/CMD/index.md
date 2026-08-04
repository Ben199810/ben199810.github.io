---
title: "MongoDB 語法指令整理與使用經驗分享"
date: 2026-03-11T17:00:33+08:00
tags: ["mongoDB", "語法指令", "資料庫管理", "查詢資料", "索引"]
draft: false
description: "MongoDB 常用語法指令整理，過程中遇到的問題以及解決方案。本文將介紹 MongoDB 的基本語法指令，包括連線指令、基本指令、查詢資料、查看正在執行的操作以及查看集合的索引等。"
---
## 前言🔖

近期因為工作上需要排查 MongoDB 的問題，過程中有使用很多的語法指令幫助自己在過程中了解問題所在，想要將近期的學習過程中所使用的 MongoDB 語法指令做一個整理，方便自己在未來需要使用的時候可以快速找到。

## MongoDB 常用語法指令📌

### 連線指令🔗

一開始最重要的就是連線到 MongoDB 的指令。如果是在 linux 環境下直接安裝 mongodb 可以直接透過 `mongosh` 連線到 MongoDB，例如：

```bash
mongosh mongodb://${username}:${password}@localhost:27017/${dbname}?authSource=admin
```

如果是使用 docker 的方式建立 MongoDB 的話，可以先進入容器內部，再使用 `mongosh` 連線到 MongoDB，例如：

```bash
docker exec -it mongodb sh
mongosh -u ${username} -p ${password} --authenticationDatabase admin
```

這裡說明一下 `--authenticationDatabase` 參數，是使用來驗證使用者的資料庫，通常會使用 `admin` 資料庫來驗證使用者的身份。如果有創建其他資料庫來驗證使用者的身份，也可以使用該資料庫來驗證，例如：

```bash
mongosh -u ${username} -p ${password} --authenticationDatabase ${authDB}
```

### 基本指令📌

成功連線到 MongoDB 後，就可以開始使用資料庫語法指令來操作 MongoDB 了。

#### 切換資料庫🔄

通常成功登入以後會預設在 `test` 資料庫，如果想要切換到其他資料庫的話，可以使用 `use` 指令，例如：

```shell
use ${dbname}
```

通常會先檢查一下目前有哪些資料庫可以使用，可以使用 `show dbs` 指令來查看，例如：

```shell
show dbs
```

#### 查看資料表🔍

成功切換到資料庫以後，可以使用 `show collections` 指令來查看目前資料庫中有哪些資料表，例如：

```shell
show collections
```

#### 資料表有多大📏

可以使用 `stats` 指令來查看資料表的大小，例如：

```shell
db.${collection}.stats()
```

預設 `scale` 的值是 1，所以回傳的的單位是 byte，如果想要以 MB 為單位的話，可以使用 `scale` 參數來指定單位，例如：

```shell
db.${collection}.stats({ scale: 1024 * 1024 })
```

以下是常用的單位：

```shell
db.${collection}.stats({ scale: 1024 }) # KB
db.${collection}.stats({ scale: 1024 * 1024 }) # MB
db.${collection}.stats({ scale: 1024 * 1024 * 1024 }) # GB
```

#### 查詢資料📊

查詢資料的指令是 `find`，可以使用 `find` 指令來查詢資料表中的資料，例如：

```shell
db.${collection}.find()
```

如果想要查詢特定條件的資料，可以在 `find` 指令中加入查詢條件，例如：

```shell
db.${collection}.find({ ${field}: ${value} })
```

如果想確認資料結構的話，可以使用 `findOne` 指令來查詢一筆資料，例如：

```shell
db.${collection}.findOne()
```

通常我們可以先查詢一筆資料來確認資料的結構，然後再根據資料的結構來撰寫查詢條件。例如：圖片(一)中的資料結構中有一個欄位叫做 `expireAt`

![文件結構](/img/posts/sql_mongodb/cmd/document_structure.png "圖片(一)")

如果想要查詢 expireAt 這個欄位存在的資料，不管 expireAt 的值為何，可以使用以下指令：

```shell
db.${collection}.find({ expireAt: { $exists: true } })
```

這樣就可以查詢資料中有存在 expireAt 這個欄位的資料了。

#### 查詢目前正在執行的操作🔍

如果想要查詢目前正在執行的操作，可以使用 `currentOp` 指令，例如：

```shell
db.currentOp()
```

更進階一點，可以搭配一些過濾條件來查詢特定的操作，例如：

```shell
db.currentOp({ $or: [{ "command.createIndexes": { $exists: true } }, { "msg": /^Index Build/ }] })
```

在這個範例中，使用 `$or` 來過濾出正在建立索引的操作，只要條件符合陣列中的任一條件，就會被查詢出來。

條件一是 `{ "command.createIndexes": { $exists: true } }`

- command 欄位通常會記錄該 operation 的指令內容（例如 find、aggregate、createIndexes…）。
- command.createIndexes 這種寫法是「點記法（dot notation）」：表示去看 command 物件底下的 createIndexes 欄位。
- $exists: true 表示：只要這個欄位存在就匹配，不管值是什麼。

條件二是 `{ "msg": /^Index Build/ }`

- msg 是 currentOp 裡常見的訊息欄位，MongoDB 會用它描述一些狀態（例如 index build 的進度訊息）。
- /^Index Build/ 是 JavaScript 正規表示式（regex）：
  - ^ 表示字串的開頭
  - Index Build 是要匹配的文字
  - 所以它會匹配「msg 以 Index Build 開頭」的 operation

#### 查詢集合的索引🔍

mongodb 每一筆資料都是一個文件(document)，這是 mongodb 中儲存資料的基本單元，這些文件會被儲存在集合(collection)中，而集合中的文件可以有索引(index)來加速查詢的速度，如果想要查看集合中的索引，可以使用 `getIndexes` 指令，例如：

```shell
db.${collection}.getIndexes()
```

##### 補充說明⭐️

索引除了直觀的加速查詢速度以外，在 DB 中也扮演資料管理與完整性的角色，索引具備以下特性：

1. **唯一性**：建立 Unique Index 可以確保索引欄位的值是唯一的，例如：e-mail 或者 username 等等。
2. **刪除過期資料**：建立 TTL Index 可以自動刪除過期的資料，例如：session 或者 token 等等。詳細的說明可以參考之前的文章 [mongoDB TTL Index 自動刪除過期資料](../TTL/index.md)。
3. **優化排序**：建立索引可以優化資料的排序，例如：按照日期或者價格等等。
4. **覆蓋查詢**：當你查詢的欄位剛好都在索引中時，MongoDB 可以直接從索引回傳結果，完全不需要讀取原始的 Document，這樣可以大幅提升查詢效率，減少磁碟 I/O 開銷。
