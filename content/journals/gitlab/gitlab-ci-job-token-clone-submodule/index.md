---
title: "使用 Git Submodule 管理公共資源倉庫，優化 GitLab CI 部署流程"
date: 2026-06-18T10:08:48+08:00
draft: false
tags: ["gitlab", "ci", "git submodule", "部署流程"]
description: "本文介紹如何使用 Git Submodule 管理公共資源倉庫，從而優化 GitLab CI 的部署流程。"
---

## 前言🔖

最近優化公司的前端專案的部署流程，發現原來的部署流程有點問題，流程大概是這樣的：

<div style="background-color:white; padding: 20px">
{{< mermaid >}}
flowchart
  classDef green fill:#dff0d8,stroke:#3c763d,stroke-width:2px,color:#000
  classDef blue fill:#d9edf7,stroke:#31708f,stroke-width:2px,color:#000
  classDef yellow fill:#fcf8e3,stroke:#8a6d3b,stroke-width:2px,color:#000
  classDef red fill:#f2dede,stroke:#a94442,stroke-width:2px,color:#000
  classDef gray fill:#ddd,stroke:#666,stroke-width:2px,color:#000

  error([CI 錯誤，終止流程]):::red
  clone_forntend_success{克隆前端倉庫成功?}:::yellow
  clone_common_assets_success{克隆公共資源倉庫成功?}:::yellow
  start([開始]):::gray --> clone_forntend_repo[克隆前端專案]:::green --> clone_forntend_success
  clone_forntend_success -- 是 --> clone_common_assets_repo[克隆公共資源倉庫]:::green
  clone_forntend_success -- 否 --> error
  clone_common_assets_repo --> clone_common_assets_success
  clone_common_assets_success -- 是 --> mv_common_assets[將公共資源移動到前端專案]:::green
  clone_common_assets_success -- 否 --> error
  mv_common_assets --> docker_build[構建 Docker 映像]:::green --> build_success{構建成功?}:::yellow
  build_success -- 是 --> push_docker_image[推送 Docker 映像到註冊表]:::green --> push_success{推送成功?}:::yellow
  build_success -- 否 --> error
  push_success -- 否 --> error
  push_success -- 是 --> finish([結束]):::gray
{{< /mermaid >}}
</div>

從上面的流程圖可以發現，CI 在建構前端專案的 Docker 映像的時候，經歷兩次克隆倉庫的過程，如果我們可以用 Git Submodule 的方式來管理公共資源倉庫，那麼就可以省去一次克隆的過程，從而優化整個部署流程。除此之外也可以確保前端專案使用固定版本的共用資源，避免因為公共資源倉庫的更新而導致前端專案出現問題。整體來說，使用 Git Submodule 的方式可以讓我們的部署流程更加高效和穩定。

## Git Submodule 的使用🚀

如何使用 Git Submodule 呢？首先，我們需要在前端專案的 Git 倉庫中添加公共資源倉庫作為子模塊：

```bash
git submodule add <公共資源倉庫的 URL> <子模塊的路徑>
```

這裡作者會建議將<公共資源倉庫的 URL>改成 SSH 的 URL，這樣開發者就可以在本機電腦的專案中統一使用 SSH 的方式克隆前端專案跟公共資源倉庫，就不用在 Clone 的過程中還要輸入帳號密碼或個人的 Access Token 了。

當我們添加完成子模塊之後，Git 會在前端專案的 Git 倉庫中創建一個特殊的文件 `.gitmodules`，這個文件用來記錄子模塊的信息。接者只需要提交這個文件到 Git 倉庫中，未來其他的小夥伴或者 CI 在克隆前端專案的時候，就可以通過 Git 一次性克隆前端專案和公共資源倉庫了。從 Git 2.13 版本及更高版本開始，--recurse-submodules 可以使用以下方式取代 --recursive：

```bash
git clone --recurse-submodules <前端專案的 URL>
```

如果子模組是在後期才新增到主專案的 Git 倉庫中，如果在本機電腦上看到主專案的 Git 倉庫中有 `.gitmodules` 文件，這個時候就可以使用以下方式來初始化子模組：

```bash
git submodule update --init --recursive
```

如果未來想要更新子模組的內容，如果團隊是透過 tags 的方式管理版本，可以使用以下方式：

```bash
cd <子模組的路徑>
git fetch --tags
git checkout tags/<標籤名稱>
```

此時，主專案會偵測到子模組的指標(Commit ID)已經改變，這個時候需要回到主專案提交這個變更。

### 如何撤銷 Git Submodule 的使用❌

如果未來想要撤銷 Git Submodule 的使用，可以按照以下步驟進行：

移除 git submodule：

```bash
git submodule deinit -f <子模組的路徑>

# 如果要一次取消所有的子模組
git submodule deinit --all
```

當執行完上面的命令之後，隱藏目錄 `.git/modules/<子模組的路徑>` 也會被刪除，`.git/config` 文件中關於子模組的配置也會被移除。
這時候就可以手動刪除子模組的目錄了：

```bash
rm -rf <子模組的路徑>
```

最後，提交這些變更到 Git 倉庫中。

## 優化過後的流程圖🗺️

導入了 Git Submodule 之後，整個部署流程就變成了下面這樣：

<div style="background-color:white; padding: 20px">
{{< mermaid >}}
flowchart
  classDef green fill:#dff0d8,stroke:#3c763d,stroke-width:2px,color:#000
  classDef blue fill:#d9edf7,stroke:#31708f,stroke-width:2px,color:#000
  classDef yellow fill:#fcf8e3,stroke:#8a6d3b,stroke-width:2px,color:#000
  classDef red fill:#f2dede,stroke:#a94442,stroke-width:2px,color:#000
  classDef gray fill:#ddd,stroke:#666,stroke-width:2px,color:#000

  error([CI 錯誤，終止流程]):::red
  start([開始]):::gray --> clone_forntend_repo[克隆前端專案]:::green --> clone_forntend_success{克隆前端倉庫成功?}:::yellow
  clone_forntend_success -- 是 --> docker_build[構建 Docker 映像]:::green --> build_success{構建成功?}:::yellow
  clone_forntend_success -- 否 --> error
  build_success -- 是 --> push_docker_image[推送 Docker 映像到註冊表]:::green --> push_success{推送成功?}:::yellow
  build_success -- 否 --> error
  push_success -- 是 --> finish([結束]):::gray
  push_success -- 否 --> error
{{< /mermaid >}}
</div>

可以發現，整個流程變得更加簡潔了，CI 在建構前端專案的 Docker 映像的時候，只需要克隆一次前端專案的 Git 倉庫就可以了，因為公共資源倉庫已經作為子模塊被包含在前端專案的 Git 倉庫中了。

也解決了未來小夥伴在開發的過程中，可以能會忘記要額外克隆公共資源倉庫的問題。

## 過程中遇到的問題💡

在實作的過程中，在地端的 Jenkins 上測試 CI 流程的時候，都沒有任何的異常。但是今天我將相同的流程重新用 GitLab CI 來測試的時候，卻遇到了一個問題，GitLab CI 在克隆前端專案的 Git 倉庫的時候，無法克隆公共資源倉庫，出現了以下的錯誤訊息：

```text
Updating/initializing submodules recursively with git depth set to 20...
Submodule 'public/image-assets' (ssh://git@gito.vastplay.online:22222/jackpot/image-assets.git) registered for path 'public/image-assets'
Synchronizing submodule url for 'public/image-assets'
Cloning into '/builds/jackpot/replay_og/public/image-assets'...
error: cannot run ssh: No such file or directory
fatal: unable to fork
fatal: clone of 'ssh://git@gito.vastplay.online:22222/jackpot/image-assets.git' into submodule path '/builds/jackpot/replay_og/public/image-assets' failed
```

可以看到，GitLab CI 在克隆公共資源倉庫的時候，出現了 `error: cannot run ssh: No such file or directory` 的錯誤訊息，代表說 gitlab runner 在執行克隆公共資源倉庫的命令的時候，無法找到 ssh 這個指令。

最根本的原因有兩個，第一個是 gitlab runner 預設的 runner helper image 根本就沒有安裝 ssh 指令提供我們做使用。如果我們使用 Dockerfile 來建構自己的 runner helper image 的話，也需要將 ssh key 跟 known_hosts 的檔案放到 runner helper image 裡面，這樣才能夠讓 gitlab runner 在執行克隆公共資源倉庫的命令的時候，能夠使用 ssh key 來驗證身份。例如下面的範例：

```dockerfile
FROM registry.gitlab.com/gitlab-org/gitlab-runner/gitlab-runner-helper:x86_64-dcfb4b66
RUN apk add openssh-client-default
RUN mkdir -p ~/.ssh
RUN ssh-keyscan -H <your git host> >> ~/.ssh/known_hosts
COPY id_rsa ~/.ssh/id_rsa
RUN chmod 600 ~/.ssh/id_rsa
```

建構完成 image 之後，可以修改 gitlab runner 的 config.toml，將 `helper_image` 改成我們自己建構的 image，這樣就可以解決這個問題了。

```toml
[[runners]]
  [runners.docker]
    helper_image = "your-custom-helper-image:latest"
```

### 問題思考💭

雖然說上面的方式可以解決這個問題，但是 gitlab 官方的文件是推薦我們可以使用 CI/CD JOB TOKEN 來克隆子模塊的 Git 倉庫的，這樣就不需要在 runner helper image 裡面安裝 ssh 指令了，也不需要在 runner helper image 裡面放入 ssh key 跟 known_hosts 的檔案了。

要怎麼實作呢？我們可以在 gitlab-ci.yml 設定以下變數，讓 gitlab runner 在克隆子模塊之前，先將 ssh url 自動替換成 https url。

```yaml
variables:
  GIT_SUBMODULE_STRATEGY: recursive
  GIT_SUBMODULE_FORCE_HTTPS: true
```

接著我們需要透過 CI/CD JOB TOKEN 來驗證身份。

#### 什麼是 CI/CD JOB TOKEN❓

當 CI/CD Pipeline 作業即將運作時，GitLab 會產生一個唯一 Token，並將其作為 $CI_JOB_TOKEN 的預定義變數提供給 Job。此 Token 僅在 Job 執行時有效。Job 結束後，Token 存取權限將被撤銷。

#### 設定子模組專案的存取權限🔐

設定好 gitlab-ci.yml 之後，還需要在子模組專案的設定頁面中，在 Settings > CICD > Job Token Permissions 中，將主專案的設定到子專案的 Job Token Permissions 中，這樣主專案的 CI/CD Pipeline 就可以使用 CI/CD JOB TOKEN 來克隆子模組專案了。

可以參考以下圖片的設定：

![job token permissions](/img/journals/gitlab/gitlab-ci-job-token-clone-submodule/job-token-permissions.png 'job token permissions')

## 結語🎯

透過 Git Submodule 的方式來管理公共資源倉庫，減少了冗餘的流程以及步驟。可以更精確的控制子模組的版本，也加速了 CI 的部署流程。當然在實作的過程中也遇到了一些問題，最後也找到了解決方案，讓整個流程變得更加順暢了。

## 參考文獻📚

- [Docker：錯誤：無法執行 ssh：沒有該檔案或目錄](https://gitlab.com/gitlab-org/gitlab-runner/-/work_items/2075)
- [CI/CD job token](https://docs.gitlab.com/ci/jobs/ci_job_token/)
