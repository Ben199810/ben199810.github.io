---
title: "Docker Bridge Network 網段範圍限制"
date: 2026-07-13T14:02:47+08:00
draft: false
description: "紀錄在工作上碰到 docker bridge network 網段範圍限制的問題，紀錄解決的方法。"
tags: ["docker", "network", "bridge network", "docker compose"]
---

## 前言

最近將公司的 api 服務轉換成 docker compose 方式部署，踩到了 docker bridge network 用盡了網段的問題，所以想要記錄一下這個坑。

## Docker Bridge 可以用的網段範圍？

當安裝好 docker 時，docker 會有一個預設的網段叫 `bridge` 會佔用 `172.17.0.0/16`，Docker 主要會在 172.16.0.0 到 172.31.255.255（B 類私有網路）這段區間進行自動切分。數量有預設上限，預設最多只能建立 31 個。

如果每個 api 的 docker compose 都使用預設的 bridge network 自動分配網段，很浪費 docker 的網段資源。所以最正確的方法是建立一個 api service 專用的 bridge network，並且指定一個網段範圍，接著所有的 api container 都使用這個網段範圍，這樣就不會浪費 docker 的網段資源。

## 建立 Docker Bridge Network

可以用 docker network create 指令建立一個新的 bridge network，並且指定網段範圍，例如：

```bash
docker network create --driver bridge --subnet=172.18.0.0/20 --gateway=172.18.0.1 api_service_network
```

如果是使用 ansible 自動化部署可以使用以下 tasks 確保網段範圍已經建立好：

```yaml
- name: ensure api_service_network bridge network exists
  community.docker.docker_network:
    name: api_service_network
    driver: bridge
    ipam_config:
      - subnet: 172.18.0.0/20
        gateway: 172.18.0.1
    state: present
  become: true
  tags: [deploy, config]
```

如果成功建立，可以用以下指令查看：

```bash
docker network ls
```

有時候會看到網段範圍已經被使用了，可以使用以下指令快速查看目前有哪些 network 且使用了哪些網段範圍：

```bash
docker network inspect $(docker network ls -q) --format '{{.Name}}: {{range .IPAM.Config}}{{.Subnet}}{{end}}'
```

![docker network inspect](/img/journals/docker/network_segment_limit/docker_network_inspect.png)

## Docker Compose 指定網段範圍

建立好共用的 bridge network 後，docker compose 可以指定使用這個網段範圍，例如：

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

設定完以後，當 container 重啟部署的時候，就不會創建新的網段範圍。會加入到建立好的 `api_service_network` 這個網段範圍中。

## 額外解決方法

調整 docker 的預設網段範圍，修改 `/etc/docker/daemon.json`，加入以下設定：

```json
{
  "default-address-pools": [{ "base": "172.17.0.0/16", "size": 24 }]
}
```

將原本比較大的網段範圍切成比較小的網段範圍，這樣就可以建立更多的 bridge network。
