---
title: "Docker"
date: 2023-07-30
description: ""
tags: ["docker"]

---

## ❓什麼是 Docker?

Docker 是一個容器化的平台，允許開發者將應用程式及其依賴打包在一個輕量級、可攜帶的容器中。這些容器可以在任何支援 Docker 的系統上運行，確保應用程式在不同環境中的一致性。

一般虛擬機器和 Docker 容器的差異，可以參考圖片（一）。

![虛擬機與 Docker 容器的差異](/img/docker/docker_vs_vm.png "圖片（一）虛擬機與 Docker 容器的差異")

### 🔍優點與缺點

兩種技術各有優缺點，選擇哪一種技術取決於具體的使用場景和需求，可以參考下方的表格來決定技術的選型。

| 技術       | 優點                                         | 缺點                                       |
| ---------- | -------------------------------------------- | ------------------------------------------ |
| 虛擬機器（VM）| 安全性較高<br>系統的選擇較多<br>應用程式不須要被拆分 | VM Image 通常比較大<br>啟動時間較長<br>資源使用較多 |
| 容器（Docker） | Image 通常比較小<br>快速啟動<br>資源使用較少 | 安全性較低<br>系統選擇受限<br>應用程式需拆分為多個服務 |

## ❓如何使用 Docker?

首先第一步要在本機電腦上安裝 Docker，可以使用 Homebrew 來安裝（以 macOS 為例）：

```bash
brew install --cask docker
```

安裝完成後，啟動 Docker 應用程式，並確認 Docker 已成功運行，可以使用以下指令來檢查 Docker 版本：

```bash
docker --version
```

### 🚀啟動第一個容器

這邊會以啟動一個簡單的 Nginx 容器為例：

```bash
docker run --name mynginx -p 8080:80 -d nginx
```

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

## 📚參考文獻

- [淺談Docker-虛擬機器和容器的差別](https://ithelp.ithome.com.tw/articles/10238498)
- [清理 Docker 的 container，image 與 volume](https://note.qidong.name/2017/06/26/docker-clean/)
