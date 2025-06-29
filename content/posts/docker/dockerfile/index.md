---
title: "Dockerfile"
date: 2023-08-27
draft: false
description: "dockerfile 相關知識"
tags: ["docker"]

---
## 前言
docker 是將 image 俗稱映像或者鏡像檔，建立容器的模擬使用環境的技術。那要如何建立 image 呢？

接著介紹本篇文章的重點 Dockerfile

## Dockerfile
Dockfile 是一個建構 image 的腳本，基於你選擇的基底映像，開始安裝在開發環境所需要的依賴以及套件等等...

建立 image 也可以保證每個開發者在進行開發時使用的環境都相同，不會導致將程式碼推上去版控，經過打包發布才發現有相容性的問題。有效的消除了在協同開發時會遇到的衝突呢～

下面提供簡單的 dockerfile 範例。下面的範例步驟使用引用 alpine image 當做基底，並且安裝 curl 套件。以 image 啟動 container 時，會執行 /bin/bash。 :point_right: `docker run -it [image] /bin/bash`

```dockerfile
# image 基底
FROM alpine
# 安裝套件或執行的 shell 
RUN apk add curl 

CMD ["/bin/bash"]
```