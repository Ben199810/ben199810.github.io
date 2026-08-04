---
title: "Docker Bridge Network 網段範圍限制"
date: 2026-07-13T14:02:47+08:00
draft: false
description: "紀錄在工作上碰到 docker bridge network 網段範圍限制的問題，紀錄解決的方法。"
tags: ["docker", "network", "bridge network", "docker compose"]
---

## 前言🔖

最近將公司的 api 服務轉換成 docker compose 方式部署，踩到了 docker bridge network 用盡了網段的問題，所以想要記錄一下這個坑。

使用 docker compose 建立 container 時，在同一份 docker compose file 裡的 container 預設都會共用一個 bridge network，這個 network 會自動被創建，通常都會是 `${service}_default`，例如 `api__default`。docker 預設會使用遮罩 `/16` 去切分網段範圍，代表每個網段可以提供 65536 個 ip 位址，這個數量對於大部分的服務來說是足夠的，但是如果每個 api 的 docker compose 都使用預設的 bridge network 自動分配網段，會很快就用完 docker 的網段資源。

## 解決方法✅

解決方法是建立一個共用的 bridge network，並且在 docker compose 裡指定使用這個共用的 bridge network，這樣就不會自動分配新的網段範圍，減少了網段資源的浪費。

## 建立 Docker Bridge Network🛜

可以用 docker network create 指令建立一個新的 bridge network，並且指定網段範圍，例如：

```bash
docker network create --driver bridge --subnet=172.18.0.0/16 --gateway=172.18.0.1 api_service_network
```

如果是使用 ansible 自動化部署可以使用以下 tasks 確保網段範圍已經建立好：

```yaml
- name: ensure api_service_network bridge network exists
  community.docker.docker_network:
    name: api_service_network
    driver: bridge
    ipam_config:
      - subnet: 172.18.0.0/16
        gateway: 172.18.0.1
    state: present
  become: true
  tags: [deploy, config]
```

先在 docker compose 建立之前，先建立好共用的 bridge network，接著可以在 docker compose 裡指定使用共用的 bridge network，這樣就不會自動分配新的網段範圍。

完成以後，可以用 ls 查看目前有哪些 network，檢查剛剛建立的 `api_service_network` 是否存在。

```bash
docker network ls

# 查看 network 詳細資訊
docker network inspect api_service_network
```

有時候創建 network 時，會出現網段衝突的問題。這時候要檢查是不是有其他的 network 已經使用了這個網段範圍，可以用以下指令查看目前所有的 network 以及網段範圍：

```bash
docker network inspect $(docker network ls -q) --format '{{.Name}}: {{range .IPAM.Config}}{{.Subnet}}{{end}}'
```

![docker network inspect](/img/journals/docker/network_segment_limit/docker_network_inspect.png)

## Docker Compose 設定⚙️

創建 networks 的字段，設定 `external: true`，代表這個 network 是外部已經存在的 network，讓 docker compose 直接使用這個已經存在的 network，而不是自動創建新的 network。

```yaml
services:
  api:
    image: api:dev
    container_name: api
    restart: unless-stopped
    ports:
      - "9249:9249"
    volumes:
      - ./config.json:/app/config.json:ro
      - ./logs:/app/logs
    env_file:
      - .env
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"
    networks:
      - default
networks:
  default:
    external: true
    name: api_service_network
```

設定以後，下一次部署 docker compose 時，container 就會加入到 `api_service_network` 這個共用的 bridge network 了。

可以用 inspect 查看 api_service_network 目前有哪些 container，確認 api container 是否已經加入到這個 network。

![docker network inspect](/img/journals/docker/network_segment_limit/docker_network_inspect_api_service_network.png)

## 遇到的問題❓

因為 docker bridge network 不能重新命名，如果想要建立的網段已經被佔用了而且也有 container 在使用的情況下，要怎麼讓服務保持運作又能夠使用新的網段呢？

首先，先建立一個比較小範圍的網段，例如 `172.19.0.0/24`，把佔用的網段範圍的 container 移到新的網段，然後再刪除舊的網段，最後再建立新的網段範圍。

先將 container 連接到新的網段再斷開舊的網段。這樣的操作可以在容器運行的狀況下進行，所以可以不停機，保持服務正常運作。

```bash
docker network connect ${NEW_NETWORK_NAME} ${CONTAINER_NAME}
docker network disconnect ${OLD_NETWORK_NAME} ${CONTAINER_NAME}
```

當所有的 container 都移到新的網段後，會發現 docker compose 原來自動建立的網段沒有被刪除，但是檢查發現已經沒有 container 在使用這個網段了，這時候可以使用 prune 指令刪除沒有使用的 network。

注意：預設的系統網路（如 bridge、host、none）不會被刪除。

```bash
docker network prune
```
