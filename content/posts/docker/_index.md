---
title: "Docker 入門指南：從基礎概念到實際操作"
date: 2023-07-30
draft: false
description: "Docker 是一個開源的容器化平台，允許開發者將應用程式及其依賴打包在一個輕量級的容器中，實現跨平台的一致運行環境。本文將介紹 Docker 的基本概念、優缺點，以及如何在本機上使用 Docker 啟動一個 Nginx 容器。"
tags: ["Docker"]
---

## 什麼是 Docker❓

Docker 是一個開源的容器化平台，可以讓開發者將應用程式以及其依賴打包在一個輕量級的容器中，實現跨平台的一致運行環境。

早期一個應用程式需要在虛擬機上運行，除了執行檔案以外，可能還需要配置服務的設定檔案、環境變數等，例如下圖: App_A 應用程式需要在虛擬機器上配置 Env_A、Env_B、Config_A，才能啟動應用程式二進制執行檔案，讓應用程式可以正常運行。App_B 應用程式需要在虛擬機器上配置 Env_B，才能啟動應用程式二進制執行檔案，讓應用程式可以正常運行。

{{< mermaid >}}
flowchart LR
subgraph VM
App_1[App_A 二進制執行檔案]
App_2[App_B 二進制執行檔案]
Env_1[環境變數A]
Env_2[環境變數B]
Config_1[設定檔案A]

App_1 -.- Env_1
App_1 -.- Env_2
App_1 -.- Config_1

App_2 -.- Env_2

classDef success fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20

class App_1,App_2 success

end
{{< /mermaid >}}

好一點的部署流程可能會自動化這些設定檔案和環境變數的配置，但是如果是運維人員需要手動配置，可能就會因為疏忽而漏掉某些設定或環境變數，導致應用程式無法正常運行。

也可能會因為特定的環境變數造成應用程式的行為不一致，導致無法運行。例如: 紅色的 Env_B，會造成 App_A 應用程式無法正常運行，這時候就需要運維人員去排查問題，找出是哪個環境變數造成的問題，這樣就會浪費很多時間。

{{< mermaid >}}
flowchart LR
subgraph VM
App_1[App_A 二進制執行檔案]
App_2[App_B 二進制執行檔案]
Env_1[環境變數A]
Env_2[環境變數B]
Config_1[設定檔案A]

App_1 -.- Env_1
App_1 -.- Env_2
App_1 -.- Config_1

App_2 -.- Env_2

classDef success fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
classDef danger fill:#ffebee,stroke:#c62828,color:#b71c1c

class App_1,Env_2 danger
class App_2 success

end
{{< /mermaid >}}

多數時候 Env 的名稱會相同但值可能不同。例如: App_A 使用 Env_B，值為 UTC，而 App_B 使用 Env_B，值為 TZ。可以看到兩個應用程式使用了一樣的 Env 是代表著時區的設定，但是值卻不同。如果部署 App_B 的時候調整了 Env_B 的值，如果 App_A 突然需要重新啟動時，就會因為 Env_B 的值被改變而導致 App_A 可能在正常的初始化階段就因為時區的設定不正確而無法正常運行。

使用 Docker 以後，可以將應用程式需要的設定檔案、環境變數和二進制執行檔案打包在一個容器中，這樣就可以確保應用程式在任何環境中都能以相同的方式運行。而且在各自的容器中，應用程式之間是相互隔離的，不會互相影響，這樣就可以避免因為環境變數或設定檔案的不同而導致應用程式無法正常運行的問題。

例如: 下圖中，App_A 應用程式和 App_B 應用程式分別在各自的容器中運行，而且代表時區的 Env_B 在各自的容器中有不同的值，這樣就不會互相影響，確保應用程式可以正常運行。

{{< mermaid >}}
flowchart LR
subgraph VM

subgraph Container_A
App_1[App_A 二進制執行檔案]
Env_1[環境變數A]
Env_2[環境變數B]
Config_1[設定檔案A]
App_1 -.- Env_1
App_1 -.- Env_2
App_1 -.- Config_1
end

subgraph Container_B
App_2[App_B 二進制執行檔案]
Env_3[環境變數B]
App_2 -.- Env_3
end

classDef success fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
classDef normal fill:#e3f2fd,stroke:#1565c0,color:#0d47a1

class App_1,App_2 success
class Env_2,Env_3 normal

end
{{< /mermaid >}}

除此之外，在共同協作的開發過程中最容易遇到的問題就是為什麼你的電腦環境可以運行，而我的電腦環境不行，這是因為每個開發者的電腦環境可能都不一樣，導致應用程式在不同的環境中運行結果不一致。這點就跟上述提到問題類似，如果可以在電腦上使用 Docker 來啟動容器，就可以隔離每個開發者電腦的環境差異。

例如: 下圖中，同事的電腦不管是直接執行二進制執行檔案，還是使用容器來執行二進制執行檔案，都可以正常運行。而我的電腦直接執行二進制執行檔案會造成無法運行的原因，就是因為我的電腦環境中缺少了某些環境變數，導致應用程式無法正常運行。但是如果使用容器來執行二進制執行檔案，就可以確保應用程式在任何人的電腦環境中都能以相同的方式運行。

{{< mermaid >}}
flowchart
subgraph 同事的電腦
Eev_1[環境變數A]
Eev_2[環境變數B]
App_1[App_A 二進制執行檔案]
App_1 -.- Eev_1
App_1 -.- Eev_2
subgraph Container_A[Container]
Env_3[環境變數A]
Env_4[環境變數B]
App_2[App_A 二進制執行檔案]
App_2 -.- Env_3
App_2 -.- Env_4
end
end

subgraph 我的電腦
subgraph Container_B[Container]
Env_5[環境變數A]
Env_6[環境變數B]
App_3[App_A 二進制執行檔案]
App_3 -.- Env_5
App_3 -.- Env_6
end
end

classDef gray fill:#f5f5f5,stroke:#9e9e9e,color:#616161
classDef yellow fill:#fff9c4,stroke:#fbc02d,color:#f57f17

class 同事的電腦,我的電腦 gray
class Container_A,Container_B yellow
{{< /mermaid >}}

這時候可能會有疑問，虛擬機器(VM)可以透過切分應用程式資料夾，在資料夾內設置對應的 .env 檔案提供應用程式讀取來解決問題，那麼 Docker 和 VM 又有什麼區別呢？

可以下圖範例來觀察 VM 和 Docker 容器的差異，可以發現 VM 上的應用程式不需要依賴在宿主機上的作業系統(OS)運行，一個 VM 環境有一個完整的作業系統，而 Docker 容器則需要依賴宿主機的作業系統來運行，這也是 Docker 的一大優勢，因為省下了 Host OS 的資源使用，讓 Docker 更輕量化，啟動速度更快！

![VM與 Docker 容器的差異](/img/posts/docker/docker-vs-vm.png "VM 與 Docker 容器的差異")

### 🔍優點與缺點

看到這裡，難道 Docker 就完全取代了虛擬機器嗎？其實不然，Docker 和 VM 都有各自的優缺點，適用於不同的場景。下面會從安全性、系統選擇、應用程式拆分、映像檔大小、啟動時間和資源使用等方面來比較 Docker 和 VM 的優缺點。

兩種技術各有優缺點，選擇哪一種技術取決於具體的使用場景和需求，可以參考下方的表格來決定技術的選型。

| 技術     | 啟動時間 | 資源使用 | 系統選擇 | 安全性 | 映像檔大小 | 應用程式拆分 | 可攜性 |
| -------- | -------- | -------- | -------- | ------ | ---------- | ------------ | ------ |
| 虛擬機器 | 慢       | 高       | 高       | 高     | 大         | 不需拆分     | 低     |
| 容器     | 快       | 低       | 限制     | 低     | 小         | 需拆分       | 高     |

## 如何使用 Docker❓

對於 Docker 有初步的認識後，接下來將會練習如何在自己電腦上使用 Docker 來啟動一個 Nginx 的容器。

環境設置:

- macOS 26.1
- Docker Desktop 4.25.0

### 安裝 DockerDesktop🛠️

首先，需要安裝工具，這裡會使用 Homebrew 來安裝 Docker。

```bash
brew install --cask docker-desktop
```

安裝完成以後，啟動 Docker Desktop 應用程式，可以看到 Docker 已成功運行，而且有 UI 的畫面，可以更方便的管理容器和映像檔。

![Docker Desktop UI](/img/posts/docker/docker-desktop.png "Docker Desktop UI")

### 拉取容器映像檔📦

Docker 啟動都會基於映像檔(Image)來啟動容器，容器的映像檔可以理解為一個應用程式的快照，裡面包含了應用程式的二進制執行檔案、設定檔案、環境變數等，這些都是應用程式運行所需要的依賴。只要執行了映像檔，就可以啟動一個容器，並且在容器中運行應用程式。

映像檔可以自己製作，也可以使用別人製作好的映像檔，這些映像檔通常會放在 Docker Hub 上，Docker Hub 是一個公共的映像檔倉庫，裡面有很多官方和社群維護的映像檔，可以直接使用。

映像檔的製作會在後面的文章接續介紹，這裡的範例會使用 Docker Hub 上官方與社群維護的映像檔，來做練習與使用。

這次的練習，需要啟動一個 Nginx 的容器，因此可以在 Docker Hub 上搜尋 Nginx，找到官方的 Nginx 映像檔，然後使用 `docker pull` 指令來下載映像檔到本機電腦上。

```bash
docker pull nginx:1.28
```

需要注意的是，如果沒有加上版本號，例如: `docker pull nginx`，預設是會下載最新的版本。

但是生產環境中通常不建議使用最新版本，因為最新版本可能會有不穩定的問題，所以最好要加上版本號，例如: `docker pull nginx:1.28`，這樣就會下載 Nginx 1.28 的版本。

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

完成以上的練習以後，如果想要清理容器可以使用 `docker rm` 指令來刪除容器。

```bash
docker rm mynginx
```

清理映像檔可以使用 `docker rmi` 指令來刪除映像檔。

```bash
docker rmi nginx:1.28
```

## 總結📝

Docker 是一個非常強大的工具，它的出現解決了很多開發者和運維人員在應用程式部署過程中遇到的問題，尤其是在環境一致性和資源使用方面。透過容器化技術，開發者可以更輕鬆地管理應用程式及其依賴，並且在不同的環境中保持一致的運行效果。

## 參考文獻📚

- [Day2 淺談Docker-虛擬機器和容器的差別](https://ithelp.ithome.com.tw/m/articles/10238498)
