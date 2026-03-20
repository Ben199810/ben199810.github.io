---
title: "Docker 入門指南：從基礎概念到實際操作"
date: 2023-07-30
description: "Docker 是一個開源的容器化平台，允許開發者將應用程式及其依賴打包在一個輕量級的容器中，實現跨平台的一致運行環境。本文將介紹 Docker 的基本概念、優缺點，以及如何在本機上使用 Docker 啟動一個 Nginx 容器。"
tags: ["docker", "容器化", "虛擬機器", "開發效率"]
---
## 什麼是 Docker❓

在過去，如果在每個開發者的個人電腦上進行開發，很容易會因為環境設定不一致，導致服務部署到生產環境時出現問題。而 Docker 的出現解決了這個問題，它允許開發者將程式碼、運行時環境、系統工具、庫等打包在一個容器中，確保在任何環境中都能以相同的方式運行。

這時候讀者們可能會有疑問，虛擬機器(VM)也可以達到類似的效果，那麼 Docker 和 VM 有什麼區別呢？下面會討論 Docker 和 VM 的差異，以及它們各自的優缺點。

可以從下圖來觀察 VM 和 Docker 容器的差異，可以發現 VM 上的應用程式不需要依賴在宿主機上的作業系統運行，而 Docker 容器則需要依賴宿主機的作業系統來運行，這也是 Docker 的一大優勢，因為省下了 OS 的資源使用，讓容器能更快地啟動和運行。

![VM與 Docker 容器的差異](/img/posts/docker/docker-vs-vm.png "VM 與 Docker 容器的差異")

### 🔍優點與缺點

上面介紹看到這裡，難道 Docker 就完全取代了虛擬機器嗎？其實不然，Docker 和 VM 都有各自的優缺點，適用於不同的場景。下面會從安全性、系統選擇、應用程式拆分、映像檔大小、啟動時間和資源使用等方面來比較 Docker 和 VM 的優缺點。

兩種技術各有優缺點，選擇哪一種技術取決於具體的使用場景和需求，可以參考下方的表格來決定技術的選型。

| 技術 | 啟動時間 | 資源使用 | 系統選擇 | 安全性 | 映像檔大小 | 應用程式拆分 | 可攜性 |
| --- | ---- | --- | --- | --- | --- | --- | --- |
| 虛擬機器 | 慢 | 高 | 高 | 高 | 大 | 不需拆分 | 低 |
| 容器 | 快 | 低 | 限制 | 低 | 小 | 需拆分 | 高 |

## 如何使用 Docker❓

對於 Docker 開始有初步的認識後，接下來將會練習如何在自己的本機電腦上使用 Docker 來啟動一個 Nginx 的容器。

### 安裝 DockerDesktop🛠️

首先，需要安裝工具，作者的電腦是 macOS，套件管理工具是 Homebrew，因此會使用 Homebrew 來安裝 Docker。

```bash
brew install --cask docker-desktop
```

在終端機上執行指令安裝 docker-desktop，安裝完成以後，啟動 Docker 應用程式，可以看到 Docker 已成功運行，而且有 UI 的畫面，可以更方便的管理容器和映像檔。

![Docker Desktop UI](/img/posts/docker/docker-desktop.png "Docker Desktop UI")

### 拉取容器映像檔📦

有了工具以後，就可以開始使用 Docker 來啟動容器了，首先可以到 Docker Hub 上搜尋想要的映像檔，Docker Hub 是一個公共的映像檔倉庫，裡面有很多官方和社群維護的映像檔，可以直接使用。

這次的練習，需要啟動一個 Nginx 的容器，因此可以在 Docker Hub 上搜尋 Nginx，找到官方的 Nginx 映像檔，然後使用 `docker pull` 指令來下載映像檔到本機電腦上。

```bash
docker pull nginx:1.28
```

需要注意的是，如果沒有加上版本號。例如 `docker pull nginx`，預設是會下載最新的版本，但是生產環境中通常不建議使用最新版本，因為最新版本可能會有不穩定的問題，所以最好要加上版本號，例如 `docker pull nginx:1.28`，這樣就會下載 Nginx 1.28 的版本。

完成以後，可以透過 Docker Desktop 的 UI 來查看已經下載的映像檔，或者使用 `docker images` 指令來查看。

![Docker Pull Nginx](/img/posts/docker/docker-pull_nginx1.28.png "Docker Pull Nginx")

### 啟動容器🚀

下載完成以後，就可以使用 `docker run` 指令來啟動一個 Nginx 的容器了，這邊會使用 `-p` 選項來將容器的 80 端口映射到本機電腦的 8080 端口，這樣就可以在瀏覽器上訪問 `http://localhost:8080` 來查看 Nginx 的歡迎頁面了。

```bash
docker run --name mynginx -p 8080:80 -d nginx:1.28
```

成功啟動以後，可以使用 `docker ps` 指令來查看正在運行的容器，或者使用 Docker Desktop 的 UI 來查看。

![Docker Run Nginx](/img/posts/docker/nginx_running.png "Docker Run Nginx")

確認 Nginx 的容器已經成功啟動以後，就可以在瀏覽器上訪問 `http://localhost:8080` 來查看 Nginx 的歡迎頁面了。

![Nginx Welcome Page](/img/posts/docker/nginx_welcome.png "Nginx Welcome Page")

### 停止容器🛑

如果要停止正在運行的容器，可以使用 `docker stop` 指令來停止容器。或者者使用 Docker Desktop 的 UI 來停止容器。

```bash
docker stop mynginx
```

完成以後，可以使用 `docker ps -a` 指令來查看所有的容器，確認 Nginx 的容器已經停止了。

![Docker Stop Nginx](/img/posts/docker/nginx_stopped.png "Docker Stop Nginx")

## 總結📝

相信通過這篇文章，讀者們對 Docker 已經有了初步的認識，了解了 Docker 的基本概念、優缺點、使用方法以及一些常見的操作技巧。Docker 是一個非常強大的工具，可以幫助開發者更高效地開發、測試和部署應用程式，尤其是在微服務架構和 DevOps 流程中，Docker 更是不可或缺的工具。

## 參考文獻📚

- [Day2 淺談Docker-虛擬機器和容器的差別](https://ithelp.ithome.com.tw/m/articles/10238498)
