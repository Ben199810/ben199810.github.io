---
title: "使用 Jenkinsfile 管理 Jenkins Pipeline"
date: 2026-02-05T15:26:08+08:00
draft: false
tags: ["jenkins", "pipeline", "jenkinsfile"]
description: "介紹如何使用 Jenkinsfile 來管理 Jenkins Pipeline，包含基礎語法與進階用法。"
---
## 前言🔖

最近換到了新的工作環境，重回了 Jenkins 的懷抱。之前在舊公司使用 Jenkins 時，體驗很差，因為 Jenkins 要裝一堆插件，還要在 UI 上配置各種參數，讓人頭痛不已。在新公司中使用 Jenkinsfile 來管理 Jenkins Pipeline，這種方式讓我感覺非常棒，因為它讓我可以把 Jenkins 的配置寫成代碼，放在版本控制系統中，這樣就可以更好地管理和追蹤變更了。

這篇文章會著重在 Jenkinsfile 的各類常用語法使用，並且會提供一些實際的範例來說明如何使用 Jenkinsfile 來管理 Jenkins Pipeline。

## Jenkinsfile 基礎語法📜

### 1️⃣變數

在 Jenkinsfile 中，可以使用 `def` 關鍵字來定義變數，例如：

```groovy
def myVar = "Hello, Jenkins!"
def updateList = ["item1", "item2", "item3"]
def desc = new StringBuilder("This is a description.")
```

第一個變數 `myVar` 是一個字符串，第二個變數 `updateList` 是一個陣列，第三個變數 `desc` 是一個 StringBuilder 對象。StringBuilder 是 Java 中的一個類，可以用來創建可變的字符串。

### 2️⃣函數

在 Jenkinsfile 中，可以定義函數來封裝一些重複使用的邏輯，例如：

```groovy
def deployToHost(String hostAddr, String sshUsername, List<String> sourceItems) {
    // 函數體
}
```

這個函數 `deployToHost` 接受三個參數：`hostAddr` 是主機地址，`sshUsername` 是 SSH 用戶名，`sourceItems` 是一個字符串列表，表示要部署的項目。

### 3️⃣pipeline 定義

接下來是整個自動化流程的定義，會使用 `pipeline` 關鍵字來定義整個 Jenkins Pipeline，例如：

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing...'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
            }
        }
    }
}
```

這個範例定義了一個包含三個階段（Build、Test、Deploy）的 Jenkins Pipeline。在每個階段中，可以使用 `steps` 來定義具體的操作，例如使用 `echo` 來輸出信息。

agent any 表示這個 Pipeline 可以在任何可用的 Jenkins 節點上運行。

ℹ️補充說明：`script` 區塊必須要放在 `steps` 裡面，否則會報錯。

## 進階語法🛠

### 1️⃣結構化參數

在 Jenkins UI 中，可以配置參數化的構建選項，這些參數可以在 Jenkinsfile 中使用。但是如果同一個 Jenkinsfile 提供很多 Pipeline 引用，每個 Pipeline 都需要配置一大堆參數，會讓人覺得很麻煩。參考圖片（一）：

!["jenkinsfile 參數化構建選項"](/img/jenkins/jenkinsfile/parameters.png "jenkinsfile 參數化構建選項")

為了解決這個問題，可以使用 `parameters` 區塊來定義結構化參數，例如：

```groovy
pipeline {
    parameters {
        text(
          name: 'versions',
          defaultValue: 'S02:v0.0.1\nS03:v0.0.1',
          description: '遊戲版本列表，格式：遊戲代碼:版本號，每行一個'
        )
        choice(
          name: 'types',
          choices: ['gameservers', 'logics'],
          description: '單款遊戲或 gameServer 選擇'
        )
    }
}
```

### 2️⃣使用變數儲存 sh 執行結果

在 Jenkinsfile 中，可以使用 `sh` 步驟來執行 shell 命令，但有時候希望能將命令的輸出結果存儲到變數中，以便後續使用。可以使用 `returnStdout: true` 來實現這一點，例如：

```groovy
def gitCommitHash = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
echo "Current Git Commit Hash: ${gitCommitHash}"
```
