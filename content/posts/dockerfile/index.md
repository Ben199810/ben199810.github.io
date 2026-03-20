---
title: "Dockerfile 入門指南：從基礎概念到實際操作"
date: 2023-08-27
description: "Dockerfile 是一個用來定義 Docker 映像檔的文本文件，通過編寫 Dockerfile，可以自動化地建構出符合需求的 Docker 映像檔。本文將介紹 Dockerfile 的基本概念、語法結構，以及如何撰寫一個簡單的 Dockerfile 來建構一個 Golang 應用程式的映像檔，最後還會介紹一些 Dockerfile 的最佳實踐和安全性考量。"
tags: ["docker", "dockerfile", "容器化", "映像檔", "開發效率"]
---
## 前言🔖

在上一篇文章中，我們介紹了 Docker 的基本概念和使用方法，也知道了 Docker Hub 上有官方以及社群維護的映像檔。實務上要如何來建構自己的映像檔呢？本文將會介紹 Dockerfile，並動手實作一個簡單的 Dockerfile 來建構一個 Golang 應用程式的映像檔，最後還會介紹一些 Dockerfile 的最佳實踐和安全性考量。

實作的專案是一個簡單的 Golang 應用程式，這個應用程式會啟動一個 HTTP 伺服器，會顯示計算機的應用程式，實作專案的程式碼放在 GitHub 上，讀者們可以透過以下連結來查看程式碼：

- [Dockerfile 實作專案程式碼](https://github.com/Ben199810/calculator)

如果想要複習上一篇文章可以透過以下連結來回顧：

{{< article link="/posts/docker/" showSummary=true compactSummary=true >}}

## 什麼是 Dockerfile❓

Dockerfile 可以想像成是一個工程藍圖，定義了如何建構一個 Docker 映像檔。它是一個純文本文件，包含了一系列的指令，每一條指令都對應著建構過程中的一個步驟。建構的過程中，會照著藍圖上的指令一步步地執行，最終產生一個符合需求的 Docker 映像檔。

Dockerfile 可以保證每次建構出來的映像檔在環境設定和依賴方面都是一致的，這對於部署和維護應用程式非常重要。Dockerfile 的指令包括了基礎映像、工作目錄、複製檔案、安裝套件、設定環境變數、暴露端口以及啟動命令等，這些指令可以組合起來定義出一個完整的建構過程。

### Dockerfile 的基本語法結構🏗️

接著，開始來逐步的講解 Dockerfile 的基本語法結構，以下面的 Dockerfile 為例：

```dockerfile
# Build stage
FROM golang:1.24-alpine AS builder

WORKDIR /app

COPY go.mod ./
RUN go mod download

COPY . .
RUN go build -o calculator .

# Run stage
FROM alpine:3.21

WORKDIR /app

COPY --from=builder /app/calculator .
COPY --from=builder /app/static ./static

EXPOSE 8080

CMD ["./calculator"]
```

1. `FROM` 首先第一個指令是 `FROM`，這個指令用來指定建構過程中使用的基礎映像，在這裡我們使用了官方的 Golang 1.24 的 Alpine 版本作為建構階段的基礎映像，並且給這個階段取了一個名字叫做 `builder`。為什麼要使用 `AS builder` 呢？後面補充會提到多階段建構的概念，所以先跳過這個部分，先專注在 `FROM` 指令的基本用法上。
2. `WORKDIR` 接下來是 `WORKDIR` 指令，這個指令用來設定工作目錄，在這裡我們設定了 `/app` 作為工作目錄，這樣後續的指令就會在這個目錄下執行。不必要使用 `RUN mkdir -p /app` 來建立目錄，因為 `WORKDIR` 指令會自動建立目錄。
3. `COPY` 指令用來將檔案從主機複製到容器中。
4. `RUN` 指令用來執行命令，這些命令會在建構過程中被執行，並且會產生對應的結果。
5. `EXPOSE` 指令用來暴露容器的端口，需要注意的是，`EXPOSE` 指令只是用來宣告容器會使用的端口，並不會實際地開放端口，實際上要開放端口還需要在啟動容器的時候使用 `-p` 選項來映射端口。
6. `CMD` 指令用來設定容器啟動時執行的命令，這個命令會在容器啟動時被執行，並且會作為容器的主進程，如果這個命令結束了，容器也會跟著結束。

### 補充說明⭐️

上述的說明簡單的介紹了每一個指令的基本用途，實際上還有很多細節和選項可以使用。這裡就先不擴充太多細節，但是有些特別的建構過程會在這裡補充說明。

#### 多階段建構🏗️

什麼是多階段建構呢？在上面的 Dockerfile 中，我們使用了兩個 `FROM` 指令，第一個 `FROM` 指令定義了一個建構階段，第二個 `FROM` 指令定義了一個運行階段。這種使用多個 `FROM` 指令的方式就叫做多階段建構。

為什麼要這麼做呢？好處是什麼？

多階段建構可以讓我們在建構過程中使用不同的基礎映像，從上面的範例來看，第一個階段使用了 Golang 的映像，這個映像包含了 Golang 的編譯工具，可以用來編譯我們的 Golang 程式碼。編譯完成以後，將編譯出來的二進位檔以及靜態資源複製到第二個階段。

在第二個階段，我們使用了更輕量級的 Alpine 映像，這個映像不包含 Golang 的編譯工具，但是包含了運行 Golang 程式所需要的環境。這樣就可以減少最終映像檔的大小，因為我們不需要在最終映像檔中包含 Golang 的編譯工具。

所以善用多階段建構可以讓我們在建構過程中使用不同的基礎映像，從而減少最終映像檔的大小，提高運行效率。

#### 映像檔的層級結構📂

在建構階段中，先執行了 `COPY go.mod ./`，然後執行了 `RUN go mod download` 指令來下載相依套件，然後又進行了 `COPY . .`，最後執行了 `RUN go build -o calculator .` 。

這時候可能有些讀者會有疑問，為什麼要進行兩次的 `COPY` 指令呢？為什麼不直接一次性地複製所有的檔案呢？

因為 Docker 的建構過程是分層的，每一條指令都會產生一個新的層級(layer)，這些層級會被快取起來，如果某一條指令的內容沒有變動，那麼 Docker 就可以直接使用快取的層級，避免重新執行這條指令。

如果我們先複製 `go.mod`，然後執行 `go mod download`，在依賴沒有變動的情況下，Docker 可以使用快取，避免每次都重新下載依賴，從而加快建構速度。

有效的利用 Docker 的快取機制，可以在生產環境的 CICD 流程中大幅提升建構效率，減少建構時間。

## 開始建構 Docker 映像檔🚀

講解完 Dockerfile 的基本語法結構以後，接下來就可以開始建構 Docker 映像檔了，建構的過程中會使用 `docker build` 指令來建構映像檔，這個指令會讀取 Dockerfile 中的指令，然後按照指令的順序來執行建構過程。

```bash
docker build -t calculator:1.0 .
```

在終端機上執行上述指令，`-t` 選項用來指定建構出來的映像檔的名稱和版本號，`.` 表示 Dockerfile 的位置在當前目錄下。

建構完成以後，可以使用 `docker images` 指令來查看已經建構出來的映像檔，或者使用 Docker Desktop 的 UI 來查看。

![Docker Images](/img/posts/dockerfile/docker-images.png "Docker Images")

## 啟動容器🚀

建構完成以後，就可以使用 `docker run` 指令來啟動一個容器了，這邊會使用 `-p` 選項來將容器的 8080 端口映射到本機電腦的 8080 端口，這樣就可以在瀏覽器上訪問 `http://localhost:8080` 來查看計算機的應用程式了。

```bash
docker run -p 8080:8080 calculator:1.0
```

![Docker Run Calculator](/img/posts/dockerfile/docker-run_calculator.png "Docker Run Calculator")

## 總結📝

相信通過這篇文章，讀者們對 Dockerfile 已經有了初步的認識，了解了 Dockerfile 的基本概念、使用方法以及一些常見的操作技巧。Dockerfile 是一個非常強大的工具，可以幫助開發者更高效地建構出符合需求的 Docker 映像檔，尤其是在微服務架構和 DevOps 流程中，Dockerfile 更是不可或缺的工具。
