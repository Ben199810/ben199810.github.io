---
title: "Docker Compose 管理多容器應用程式的最佳利器"
date: 2026-09-07T10:18:11+08:00
draft: true
description: ""
---

## 前言🔖

透過前幾篇文章，我們已經掌握了 Docker 的基本概念與操作，在實務上一個軟體系統的組成往往不會只有單一個容器，而是由多個容器所組成，這些容器之間可能有著相依性，並且需要透過網路進行溝通。如果管理多個容器還在使用 `docker run` 指令的方式，就算有使用自動化管理工具，也會因為冗長的指令而讓人感到困擾。這時候就是本篇文章的主角 Docker Compose 上場的時候了。

Docker Compose 可以做什麼呢？如果我們將 Dockerfile 比喻成一個容器的藍圖，那麼 Docker Compose 可以想像是一個小型社區的藍圖，例如社區裡面有著管理室、停車場、游泳池、健身房等設施，這些設施之間有著相依性，並且需要透過道路進行溝通。Docker Compose 就是用來管理這個小型社區的工具，它可以幫助我們定義多個容器之間的相依性，並且透過網路進行溝通。

## Docker Compose 的安裝🔨

在前幾篇文章練習中，有安裝 Docker Desktop，Docker Desktop 內建了 Docker Compose，因此不需要額外安裝。如果是獨立安裝 Docker Engine 的使用者，則需要額外安裝 Docker Compose。Docker Compose 的安裝方式可以參考官方文件：[Install Docker Compose](https://docs.docker.com/compose/install/)

## 練習📝

練習會分成兩個部分，會先單獨使用 Docker Compose 建立一個 php 容器，然後再建立一個 nginx 以及 phpmyadmin 的容器，並且透過 Docker Compose 來管理這三個容器之間的相依性。

### 建立 php 容器📌

首先，我們需要先建立 `docker-compose.yaml` 檔案，並且在檔案中定義 php 容器的相關設定，以下是範例內容：

```yaml
version: '3.8'
services:
  php:
    image: php:8.5.10-alpine3.24
    container_name: php_container
    ports:
      - "8080:80"
```