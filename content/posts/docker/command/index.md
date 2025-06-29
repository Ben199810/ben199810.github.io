---
title: "Docker 指令"
date: 2023-07-30
draft: false
description: "docker 常用指令筆記"
tags: ["docker"]

---
## 匯出/入映像檔
:star: export 可以匯出 container 已變更的設定

:star: save 單純匯出 image

:star: 這裡要注意 export 對應 import ; save 對應 load

```
docker export [image] > [filename].tar
```

```
docker import < [filname].tar
```

---

```
docker save [image]:[tag] > [filname].tar
```

```
docker load < [filname].tar
``` 

<br>

## 在容器裡執行應用程序
:star: docker `start`、`stop`、`restart`

```
docker run [image] /bin/echo "Hello world"
```

<br>

## 與容器進行交互
```
-t：終端機
-i：准許你與容器交互
-d：在背景執行
exit 或 ctrl+d：離開容器
```

```
docker run -i -t [image] /bin/bash
```

<br>

## 在容器裡查看當前系統版本信息。
```
cat /proc/version
```

<br>

## 查看運行的容器
```
-a：顯示所有容器
```

```
docker ps
```

<br>

## 查看容器內的標準輸出
```
-f：持續查看
```

```
docker logs [container]
```

<br>

## 進入容器
:star: 如果使用 attach 進入容器，退出時會導致容器停止

```
docker attach [container]
```

```
docker exec -it [container] /bin/bash
```

<br>

## 查看 image 、 container 詳細大小。
```
docker system df -v
```

<br>

## 查看容器啟動進程
```
docker top [container]
```

<br>

## container 資源使用狀況
```
docker stats 
```

<br>
    
## docker-compose 針對特定容器重啟
```
 docker-compose up --detach --build [service_name]
```

<br>

## docker 清理技巧
[清理 Docker 的 container，image 與 volume](https://note.qidong.name/2017/06/26/docker-clean/)

:star: prune操作是批量刪除類的危險操作，使用 y 確認。不想要輸入可以添加 -f，慎用!

### 清除所有停止運行的容器
```
docker container prune
```

### 清理所有 <none> image 
```
docker image prune
```

### 清理未使用的 image
```
docker image prune -a
```

### 清理所有無用的 volumes
```
docker volume prune
```
    
<br>

## Dcokerfile 與 Docker-compose
[Day14 Dockerfile & Docker-Compose](https://ithelp.ithome.com.tw/articles/10241810)

### 對 Docker Image 做反編譯成 Dockerfile
沒有命令直接通過 image 就能反編譯，獲得 Dockerfile
    
但是我們可以使用 docker history 命令，進行反推

```
--format：自定義輸出格式
--no-trunc：CREATED BY 列完整顯示
```

使用 `history` 
```
docker history [image:tag]
```

```
docker history [image:tag] --format "table {{.ID}}\t{{.CreatedBy}}" --no-trunc
```     