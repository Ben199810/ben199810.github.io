---
title: "Jenkinsfile 範例與應用"
date: 2026-02-05T15:26:08+08:00
draft: false
tags: ["Jenkins"]
description: "Jenkinsfile 範例與應用，介紹如何在 Jenkins 中使用程式碼管理 Pipeline 配置，包括變數、結構化參數、Shell 執行結果以及構建信息的顯示。"
---
## 前言🔖

之前習慣將 Jenkins 的配置都放在 UI 上，更好的方式應該要將這些配置寫成程式碼，這樣可以更方便地管理和追蹤變更。我會記錄在工作上常用的 Jenkinsfile 寫法和應用。

要開始寫之前，先了解 Jenkinsfile 的整體結構，因為是一個描述整個 Jenkins Pipeline 的腳本，最外層就是使用 `pipeline` 關鍵字包裹整個流程。

接著跟 Gitlab CI 很像，需要用 `stages` 來定義不同的階段，每個階段可以包含多個步驟。`steps` 的區塊內還可以切成更小的 `script` 區塊。
```groovy
pipeline {
  agent any // 任意節點都可以執行
  stages {
    stage('Example') {
      steps {
        script {
          echo 'Hello, Jenkins!'
        }
      }
    }
  }
}
```

## 變數📌

在 Jenkinsfile 中，可以使用 `def` 關鍵字來定義變數。例如: 第一個變數 `myVar` 是一個字符串，第二個變數 `updateList` 是一個陣列，第三個變數 `desc` 是一個 StringBuilder 對象。StringBuilder 是 Java 中的一個類，可以用來創建可變的字符串。
```groovy
def myVar = "Hello, Jenkins!"
def updateList = ["item1", "item2", "item3"]
def desc = new StringBuilder("This is a description.")
```

變數定義在哪一個位置也很重要，會影響作用域。這邊舉一個例子來說明。可以看到在 `stage` 內部定義的變數，只能在該 `stage` 中使用，而在 `stage` 外部定義的變數，則可以在整個 `pipeline` 中使用。
```groovy
def globalVar = "I am a global variable"
pipeline {
  agent any
  stages {
    stage('Example') {
      def localVar = "I am a local variable"
      steps {
        script {
          echo "Global variable: ${globalVar}"
          echo "Local variable: ${localVar}"
        }
      }
    }
    stage('Another Example') {
      steps {
        script {
          echo "Global variable: ${globalVar}"
          // echo "Local variable: ${localVar}" // 這裡無法訪問 localVar，會報錯
        }
      }
    }
  }
}
```

## 結構化參數📌

在 Jenkins UI 中，可以配置參數化的構建選項，這些參數可以在 Jenkinsfile 中使用。但是如果同一個 Jenkinsfile 提供很多 Pipeline 引用，每個 Pipeline 都需要配置一大堆參數，會讓人覺得很麻煩。參考圖片如下:

!["jenkinsfile 參數化構建選項"](/img/posts/jenkins/jenkinsfile/parameters.png "jenkinsfile 參數化構建選項")

為了解決這個問題，可以使用 `parameters` 區塊來定義結構化參數，例如以下的範例:

這裡設置了我最常用的三種參數：文字參數、選擇參數和布林參數。
```groovy
pipeline {
  parameters {
    text(
      name: 'versions',
      defaultValue: 'v0.0.1',
      description: '遊戲版本'
    )
    choice(
      name: 'gamesId',
      choices: ['S01', 'S02'],
      description: '遊戲 ID'
    )
    booleanParam(
      name: 'isRelease',
      defaultValue: false,
      description: '是否為發佈版本'
    )
  }
}
```

## 使用變數儲存 shell 執行結果📌

在 Jenkinsfile 中，可以使用 `sh` 步驟來執行 shell 命令，但有時候希望能將命令的輸出結果存儲到變數中，以便後續使用。可以使用 `returnStdout: true` 來實現這一點，例如：
```groovy
pipeline {
  agent any
  stages {
    stage('Get Git Commit Hash') {
      steps {
        script {
          def gitCommitHash = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
          echo "Current Git Commit Hash: ${gitCommitHash}"
        }
      }
    }
  }
}
```

## 透過 Edit Build Information 清楚的顯示構建信息📌

我通常會先定義一個變數來存儲我要顯示的建構訊息，例如: Gitlab Repository、分支名稱、提交 Hash 等等，然後在 pipeline 中使用這些變數來更新構建信息。接著，只需要將 currentBuild.description 設置為 desc 的內容，就可以在 Jenkins UI 中清楚地看到構建信息了。
```groovy
def desc = new StringBuilder("Build Information:\n")
pipeline {
  agent any
  post {
    always {
      script {
        desc.append("Gitlab Repository: ${env.GIT_URL}\n")
        desc.append("Branch: ${env.GIT_BRANCH}\n")
        desc.append("Commit Hash: ${env.GIT_COMMIT}\n")
        currentBuild.description = desc.toString()
      }
    }
  }
}
```

這樣帶來的好處是可以快速了解每次構建的關鍵信息，方便排查問題和追蹤版本。也可以快速地透過篩選 Jenkins 構建記錄來找到特定的構建記錄，總之好處多多。

!["Edit Build Information"](/img/posts/jenkins/jenkinsfile/edit_build_info.png "Edit Build Information")

## 捨棄舊建置📌

Jenkins 可以在 Pipeline UI 中配置「捨棄舊建置」策略，可以保留建構歷史的最新幾個版本，或者保留一定天數內的建構，從而避免磁碟空間被舊建置佔滿。

!["捨棄舊建置"](/img/posts/jenkins/jenkinsfile/build_discarder.png "捨棄舊建置")

這個策略也可以在 Jenkinsfile 中通過 `buildDiscarder` 來配置，我習慣寫在 Jenkinsfile 中，因為有一些 CI 我集成了比較多的服務。可以保留比較多的建置歷史跟天數，確保重要的構建記錄不會被過早刪除。
```groovy
pipeline {
  agent any
  options {
    buildDiscarder(logRotator(numToKeepStr: '200', daysToKeepStr: '14', artifactNumToKeepStr: '50', artifactDaysToKeepStr: '14', removeLastBuild: false))
  }
  stages {
    stage('Example') {
      steps {
        echo "Hello, World!"
      }
    }
  }
}
```

## Credentials📌

在 Jenkins 中，我們可以使用 Credentials 來安全的存儲和管理敏感信息，例如 API 金鑰、密碼、SSH 金鑰等，避免將這些信息硬編碼在 Jenkinsfile 中。而且在 CI 流程中調用 Credentials 時，會將這些敏感信息隱藏起來，確保安全性。

!["Credentials"](/img/posts/jenkins/jenkinsfile/credentials.png "Credentials")

下列會列舉如何在 Jenkinsfile 中使用 Credentials 取得 GitLab API Token 然後在 shell 中使用它查詢 Gitlab 專案的 Webhook。
```groovy
pipeline {
  agent any
  stages {
    stage('Use Credentials') {
      steps {
        withCredentials([
          string(credentialsId: 'GITLAB_API_TOKEN', variable: 'GITLAB_API_TOKEN')
        ]) {
          sh '''
            HOOKS_RESPONSE=$(curl --silent --show-error --fail-with-body \
            --header "PRIVATE-TOKEN: ${GITLAB_API_TOKEN}" \
            "${API_BASE}?per_page=100&page=${PAGE}")
          '''
        }
      }
    }
  }
}
```