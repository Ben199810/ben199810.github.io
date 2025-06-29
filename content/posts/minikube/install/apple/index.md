---
title: "minikube 安裝 for M系列晶片 Mac"
date: 2023-09-24
draft: false
description: "minikube 的環境與安裝"
tags: ["k8s", "minikube", "mac", "m1", "m2"]

---
## 前言
最近趁著 BTS 學生教育方案入手了 macbook pro m2 版本，因此也想要在上面安裝 minikube 來練習 k8s 的操作。但在安裝的過程中，發現了一些問題，因此紀錄一下。

## 問題
在安裝的過程中，發現目前 [vitrualbox](https://www.virtualbox.org/wiki/Downloads) 還不支援 m1 與 m2 版本的 mac。所以找了其他的虛擬機軟體

其中也有使用 [hyperkit](https://minikube.sigs.k8s.io/docs/drivers/hyperkit/) 來安裝的方式。但也是不行。

## 解決方案
後來找到 [Qemu](https://www.qemu.org/) 這個虛擬機軟體，這邊簡單介紹。

QEMU 是一種模擬器，它能夠完成使用者程式模擬和系統虛擬化模擬：

* 使用者程式模擬：QEMU 能夠將為一個平台編譯的二進位檔案運行在另一個不同的平台。
* 系統虛擬化模擬：QEMU 能夠模擬一個完整的系統虛擬機，該虛擬機有自己的虛擬CPU、晶片組、虛擬記憶體以及各種虛擬外部設備，能夠為虛擬機中運行的作業系統和應用軟體呈現出與實體電腦完全一致的硬體視圖。QEMU能夠模擬 x86、`ARM`、MIPS、PPC 等多個平台。

沒錯，可能有讀者發現了重點，因為 m1 與 m2 是 `ARM` 架構，因此可以使用 Qemu 來模擬我們所需要的 VM 環境。

## 安裝

先安裝 Qemu

```bash
brew install qemu
```

接著設定 Qemu socket_vvmnet

```bash
brew install socket_vmnet
brew tap homebrew/services
HOMEBREW=$(which brew) && sudo ${HOMEBREW} services start socket_vmnet
```

就可以啟動我們的環境啦！

```bash
minikube start --driver qemu --network socket_vmnet
```

## 參考資料
[How to Setup Minikube on MAC M1/M2](https://devopscube.com/minikube-mac/)