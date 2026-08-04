---
title: "使用 Docker 設置 GitLab CI/CD 與 Runner"
date: 2026-02-06T16:53:31+08:00
draft: false
description: ""
---

## 前言🔖

近期在構思雲上部署方案，決定使用 Gitlab CI/CD 來實現自動化部署。因為之後會調整 GitFlow 的部署方式，所以 Gitlab CI/CD 能夠自動依照分支名稱來部署到不同的環境，這樣可以大大提升部署效率和可靠性。

## GitLab Runner 的設置🔧

為了讓 GitLab Runner 能夠在 Docker 環境中運行，我們需要確保 Runner 的配置允許使用 Docker-in-Docker（DinD）。這樣 Runner 就能夠在構建過程中使用 Docker 命令來構建和推送映像。

### 建置 Runner 容器📦

使用 Dockerfile 來建置 Runner 容器，確保安裝了 Docker CLI 並配置好必要的環境變量。

```yaml
services:
  gitlab-runner:
    container_name: gitlab-runner
    image: "gitlab/gitlab-runner:latest"
    restart: always
    environment:
      DOCKER_CACHE_DIR: /cache
      DOCKER_DISABLE_CACHE: "false"
      DOCKER_PRIVILEGED: "true"
      DOCKER_TLS_VERIFY: "false"
      RUNNER_CACHE_DIR: /cache
      RUNNER_EXECUTOR: docker
    volumes:
      - ./ssl/example_com.crt:/etc/gitlab-runner/certs/example_com.crt:ro
      - /var/run/docker.sock:/var/run/docker.sock
      - ./runner/config:/etc/gitlab-runner
```

executor 是 runner 的執行器類型，一般用的比較多的是 shell 或 docker，這裡我們選擇 docker。

讓人比較困惑的是其它一些 executor，如 Docker-SSH、Docker-SSH+machine 等，這些 executor 從 GitLab Runner 10.0 開始，兩者就被廢棄了，並且在後續的版本中移除。

還有 Docker machine，這個概念本來是 Docker 提出的，但是後面同樣被 Docker 棄用了，只是 GitLab 為了向前兼容保留了下來。

### Docker in Docker 的配置⚙️

在容器內部執行 Docker 指令，一般有兩種方式：

  1. 掛載宿主機的 Docker Socket：這種方式比較簡單，直接將宿主機的 Docker Socket 掛載到 Runner 容器中，Runner 就可以直接使用宿主機的 Docker 服務來構建和推送映像。
  2. 容器內部有自己的一套 Docker 環境，使用 docker:dind 的 image 來運行 DinD 服務，可以使用它作為主容器，也可以作為其他容器的服務容器（與其他服務之間通信）。

如前面所述，以 Docker 方式安裝 Runner，且 executor 設置為 docker，那麼就要設置 DinD。因為 Runner 只是啟動新容器，如果不要求 Runner 容器內部啟動 DinD 服務，我們可以採用第一種方式，直接掛載宿主機的 Docker Socket。

另外，如果 Docker executor 在 CI/CD job 中涉及到 Docker 指令，那麼也要 Docker-in-Docker。記得要配置啟動容器的特權模式（privileged: true），這樣才能讓 DinD 正常運行。

接下來使用任一種方式實現 DinD。

- 在 config.toml 中新增設定 volumes = ["/cache", "/var/run/docker.sock:/var/run/docker.sock"]。
- 或者在 .gitlab-ci.yml 中指定 docker:dind

  ```yml
  services:
    - docker:dind
  ```

### Runner 設定檔⚙️

Runner 的設定檔位於 `./runner/config` 目錄下，這裡需要配置 Runner 的註冊信息，包括 GitLab 的 URL、註冊令牌、執行器類型等。

```toml
concurrent = 1
check_interval = 0
shutdown_timeout = 0

[session_server]
  session_timeout = 1800

[[runners]]
  name = "docker-runner"
  url = "https://example.com/"
  id = 1
  token = "xxx-xxx.xxxx.xxxxxxx"
  token_obtained_at = 2026-02-02T08:08:00Z
  token_expires_at = 0001-01-01T00:00:00Z
  tls-ca-file = "/etc/gitlab-runner/certs/example_com.crt"
  executor = "docker"
  [runners.cache]
    MaxUploadedArchiveSize = 0
    [runners.cache.s3]
    [runners.cache.gcs]
    [runners.cache.azure]
  [runners.docker]
    tls_verify = false
    image = "docker:29.2.0-alpine3.23"
    privileged = true
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/cache"]
    cache_dir = "/cache"
    shm_size = 0
    network_mtu = 0
```

## 參考文獻📚

- [gitlab-runner 中的 Docker-in-Docker](https://www.cnblogs.com/newton/p/17408489.html)
