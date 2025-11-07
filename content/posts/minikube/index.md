---
title: "使用 Minikube 在本機電腦模擬 Kubernetes 環境（Mac M1/M2）"
date: 2023-09-24
draft: false
description: ""
tags: ["kubernetes", "minikube", "mac", "m1", "m2"]

---

## 📝介紹

Minikube 是一個輕量級的 Kubernetes 環境，主要用於本地開發和測試。它可以在本機電腦上啟動一個單節點的 Kubernetes 集群，讓開發者可以快速地部署和測試應用程式。

Minikube 支援多種虛擬化技術，包括 VirtualBox、VMware、KVM、Hyper-V 等等。它可以在 Windows、macOS 和 Linux 上運行。

## 🖥️Qemu 虛擬化驅動

介紹的部分有提到 Minikube 支援多種虛擬化技術，而在 macOS 上，特別是使用 Apple Silicon（M1、M2）晶片的 Mac 電腦上，傳統的虛擬化技術如 VirtualBox 並不支援 ARM 架構（至少我出這篇文章的時候還沒有ＱＱ）。

因此，我們可以使用 Qemu 作為 Minikube 的虛擬化驅動程式。

### 📖Qemu 簡介

Qemu 是一個開源的虛擬化軟體，可以模擬多種硬體架構，包括 x86、ARM、MIPS 等等。它可以用於虛擬化和模擬不同的作業系統和應用程式。

Qemu 的主要功能包括：

- 使用者程式模擬：QEMU 能夠將為一個平台編譯的二進位檔案運行在另一個不同的平台。
- 系統虛擬化模擬：QEMU 能夠模擬一個完整的系統虛擬機，該虛擬機有自己的虛擬CPU、晶片組、虛擬記憶體以及各種虛擬外部設備，能夠為虛擬機中運行的作業系統和應用軟體呈現出與實體電腦完全一致的硬體視圖。QEMU能夠模擬 x86、ARM、MIPS、PPC 等多個平台。

### 🔧安裝

在 macOS 上安裝 Minikube 和 Qemu，可以使用 Homebrew 來簡化安裝過程。
首先，確保你已經安裝了 Homebrew。如果還沒有安裝，可以參考 [Homebrew 官方網站](https://brew.sh/) 進行安裝。

```bash
brew install minikube
brew install qemu
```

### 🌐Socket_vmnet 網路驅動

Qemu 提供兩種網路選項：

- socket_vmnet
- builtin（內建網路）

socket_vmnet 提供 Minikube 完整的網路功能，而 builtin 網路則有一些限制。例如：service 和 tunnel 等指令不可用。

```bash
brew install socket_vmnet
brew tap homebrew/services
HOMEBREW=$(which brew) && sudo ${HOMEBREW} services start socket_vmnet
```

## 🚀啟動

上述所有的套件安裝完成後，可以使用以下命令啟動 Minikube，並指定使用 Qemu 作為虛擬化驅動程式。

```bash
minikube start --driver qemu --network socket_vmnet
```

## 📚參考文獻

- [How to Setup Minikube on MAC M1/M2](https://devopscube.com/minikube-mac/)
- [Minikube QEMU](https://minikube.sigs.k8s.io/docs/drivers/qemu/)
