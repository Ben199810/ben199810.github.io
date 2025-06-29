---
title: "GitLab CICD"
date: 2023-09-22
draft: false
description: "gitlab cicd 基礎"
tags: ["gitlab", "cicd"]
---

## 前言
最近因為公司有在進行 GitLab 轉移，所以要重新建構 CICD，提供比較好維護的 CI modules，讓所有的組能夠通用，達到流程簡化的目的。有開始用一些比較進階的 CICD 寫法所以透過寫筆記，提升自己的印象。

## 概念
使用 gitlab-ci 建立的自動化流程，稱作 `pipeline` 中文意思是流水線。就像設定好一個生產線一樣十分有趣。
![gitlab pipeline](/img/gitlab/pipeline/pipeline.png)

這邊已經知道了 pipeline，那由誰執行 pipeline 的流程呢？答案是 `gitlab runner`。當有 pipeline 觸發且需要執行時，會有 job 產生，這些 job 就會分配給 runner 去執行囉！
![gitlab runner](/img/gitlab/pipeline/runner.jpeg)

## 基礎 CICD
了解概念之後，就可以開始寫自己的 CICD 了！那一般的 CICD 流程是什麼呢？一般來說會有以下基本元素：

:one: Stage

:two: Job

:three: Script

可以看到下面的 yaml 是一個基礎的 pipeline 範例，可以看到有三個 stage，分別是 build、test、deploy，每個 stage 底下都有一個 job，每個 job 底下都有一個 script，這個 script 就是要執行的指令。

範例：
```yaml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    # 定義 build 階段的指令
    - echo "Building the application"
    - docker build -t $IMAGE_NAME:$TAG .

test:
  stage: test
  script:
    # 定義 test 階段的指令
    - echo "Running tests"

deploy:
  stage: deploy
  script:
    # 定義 deploy 階段的指令
    - echo "Deploying to production"
    # 在實際情況下，這裡可以是部署到 Kubernetes、AWS、GCP 等的相應指令
    # 也可以使用 Helm 進行部署

```
