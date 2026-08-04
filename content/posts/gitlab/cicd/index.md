---
title: "GitLab CICD"
date: 2023-09-22
draft: false
description: "gitlab cicd 基礎"
tags: ["gitlab", "cicd"]
---

## 介紹

GitLab 是一個開源的 DevOps 平台，提供了版本控制、CI/CD、代碼審查等功能。它的 CI/CD 功能可以幫助開發者自動化軟體開發流程，提高開發效率和質量。

GitLab 的 CI/CD 功能基於 GitLab Runner，允許開發者定義自動化的工作流程，從代碼提交到部署生產環境都可以自動化完成。

GitLab CI/CD 的配置文件是 `.gitlab-ci.yml`，這個文件定義了 CI/CD 的工作流程，包括各個階段（stages）、任務（jobs）和執行的腳本（scripts）。開發者可以根據自己的需求定義不同的工作流程，並且可以在不同的階段中執行不同的任務。

## 基本配置

以下是一個簡單的 `.gitlab-ci.yml` 配置範例，包含了三個階段：test、build 和 deploy。

```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  script:
    # 定義 test 階段的指令
    - echo "Running tests"
    # 執行單元測試、程式碼品質檢查等
    - npm test
    - npm run lint

build:
  stage: build
  script:
    # 定義 build 階段的指令
    - echo "Building the application"
    - docker build -t $IMAGE_NAME:$TAG .
  # 只有當測試通過後才執行 build
  needs: ["test"]

deploy:
  stage: deploy
  script:
    # 定義 deploy 階段的指令
    - echo "Deploying to production"
    # 在實際情況下，這裡可以是部署到 Kubernetes、AWS、GCP 等的相應指令
    # 也可以使用 Helm 進行部署
  # 只有當 build 成功後才執行 deploy
  needs: ["build"]
```

## 進階配置

在生產環境中，通常需要更複雜的配置，例如：配置環境變數、建構 mysql 資料庫、redis 等服務。

```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  services:
    - name: mysql:5.7
      alias: db
    - redis:latest
      alias: redis
  variables:
    MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    MYSQL_DATABASE: ${MYSQL_DATABASE}
    REDIS_PASSWORD: ${REDIS_PASSWORD}
  script:
    - echo "Running tests"
    - npm test
    - npm run lint

build:
  stage: build
  script:
    - echo "Building the application"
    - docker build -t $IMAGE_NAME:$TAG .
  needs: ["test"]

deploy:
  stage: deploy
  script:
    - echo "Deploying to production"
  needs: ["build"]
```

### parallel:matrix

⚠️ 對於 runner 的配置，必須要有多台 runner 或者配置單台 runner 配置支援同時執行多個任務。

⚠️ 矩陣的排列數不能超過 200

`parallel` 可以在單一的 pipeline 中同時執行多個任務，這對於需要在多個環境或配置下運行相同任務的情況非常有用。

如果需要在不同的 Node.js 版本和環境下運行測試，可以使用 `parallel:matrix` 來定義一個矩陣，這樣可以在不同的配置下同時運行相同的任務。

```yaml
test:
  stage: test
  script:
    - echo "Running tests"
  parallel:
    matrix:
      - NODE_VERSION: [10, 12, 14]
      - ENV: [development, production]
```

## 參考

- [Parallel](https://docs.gitlab.com/ci/yaml/#parallelmatrix)
