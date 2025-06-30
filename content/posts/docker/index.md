---
title: "Docker"
date: 2023-07-30
description: "docker 常用指令筆記"
tags: ["docker"]

---
## 匯出/匯入

export 和 save 都是用來匯出 docker 的映像檔，但是有些不同之處：

- export 可以匯出在容器中已變更的設定，例如安裝的軟體或修改的配置檔案。
- save 單純匯出映像檔，不包含在容器中已變更的設定。

在使用上要注意，如果映像檔使用 export 匯出，則需要使用 import 匯入；如果使用 save 匯出，則需要使用 load 匯入。

```bash
docker export image > filename.tar
docker import < filename.tar
```

```bash
docker save image > filename.tar
docker load < filename.tar
```

## 與容器進行交互

通常我們會使用 `docker run` 指令來啟動容器，如果需要與容器進行交互，可以使用以下選項：

```bash
docker run -it image /bin/bash
```

如果要退出容器，可以使用 `exit` 或 `ctrl+d`。

## 查看容器

如果要查看正在運行的容器，可以使用以下指令 `docker ps`，如果要查看所有的容器（包括已停止的容器），可以使用 `docker ps -a`。

```bash
docker ps -a
```

## 查看容器內的標準輸出

如果要查看容器內的標準輸出，可以使用 `docker logs` ，但是通常我們會持續的觀察容器的標準輸出，因此可以使用 `-f` 選項來持續查看。

```bash
docker logs -f container
```

## 查看容器啟動進程

```bash
docker top container
```

## 容器資源使用狀況

```bash
docker stats
```

## 清理技巧

⭐ prune操作是批量刪除類的危險操作，使用 y 確認。不想要輸入可以添加 -f，慎用!

### 清除所有停止運行的容器

```bash
docker container prune
```

### 清理未使用的映像檔

```bash
docker image prune 
```

### 清理所有無用的卷

```bash
docker volume prune
```

## 參考

[清理 Docker 的 container，image 與 volume](https://note.qidong.name/2017/06/26/docker-clean/)
