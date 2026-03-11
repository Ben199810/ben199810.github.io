---
title: "MongoDB 語法指令"
date: 2026-03-11T17:00:33+08:00
draft: true
description: "MongoDB 常用語法指令整理"
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

#### 補充說明⭐️

`--authenticationDatabase` 參數使用來驗證使用者的資料庫，通常會使用 `admin` 資料庫來驗證使用者的身份。如果有創建其他資料庫來驗證使用者的身份，也可以使用該資料庫來驗證，例如：

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

如果想要查詢 expireAt 這個欄位存在的資料，不管 expireAt 的值為何，可以使用以下指令：

```shell
db.${collection}.findOne({ expireAt: { $exists: true } })
```

這樣就可以查詢到一筆資料中 expireAt 這個欄位存在的資料了。

#### 查詢集合的索引🔍

mongodb 每一筆資料都是一個文件(document)，這是 mongodb 中儲存資料的基本單元，這些文件會被儲存在集合(collection)中，而集合中的文件可以有索引(index)來加速查詢的速度，如果想要查看集合中的索引，可以使用 `getIndexes` 指令，例如：

```shell
db.${collection}.getIndexes()
```
