---
title: "省錢大作戰 - 單一節點部署 Redis Cluster"
date: 2026-09-23T10:35:40+08:00
draft: false
description: ""
tags: ["Redis", "Redis Cluster"]
---

## 前言 🔖

在生產環境前，通常也會有 2 到 3 個環境，例如開發環境、測試環境和預發布環境，用於不同階段的應用測試和驗證。小團隊常常會有成本上面的考量，如果開發環境也跟生產環境一樣配置，但實際上可能並不需要那麼高的資源配置，這時候我們可以使用單節點部署的方式來節省資源，省下不必要的開銷。

## Docker Compose 🐳

我們會使用 Docker Compose 來搭建多個 Redis Container，再通過配置文件來管理它們的啟動、停止和網絡連接。可以快速的在任何的單一節點環境快速的搭建 Cluster 群集。非常適合用於開發和測試環境。

要部署的 Redis 群集是 3Master + 3Slave 的單節點配置。

端口配置如下：
- Master-1: 6379 (對外), 16379 (Cluster)
- Master-2: 6380 (對外), 16380 (Cluster)
- Master-3: 6381 (對外), 16381 (Cluster)
- Slave-1: 6382 (對外), 16382 (Cluster)
- Slave-2: 6383 (對外), 16383 (Cluster)
- Slave-3: 6384 (對外), 16384 (Cluster)

🟡 注意: Cluster 集群最少需要 3 個 Master 節點。

這裡只會展示 Master-1 和 Slave-1 的配置，其餘的 Master 和 Slave 配置基本上類似，只需根據需求修改對應的端口和配置文件即可。

除此之外，可以看到範例還有配置了一個 Redis Exporter，可以讓我們監控 Redis 群集的運行狀態和性能指標。

```yaml
services:
  redis-master-1:
    container_name: redis-master-1
    image: redis:6.0.16
    command: ["/redis-entrypoint.sh"]
    volumes:
      - ./master-1/data:/data
      - ./redis-master-1.conf:/usr/local/etc/redis/redis.conf
      - ./redis-entrypoint.sh:/redis-entrypoint.sh:ro
    ports:
      - "6379:6379"
      - "16379:16379"
    restart: always
    deploy:
      resources:
        limits:
          cpus: "0.3"
          memory: "32M"
        reservations:
          cpus: "0.15"
          memory: "16M"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
  ...

  redis-slave-1:
    container_name: redis-slave-1
    image: redis:6.0.16
    command: ["/redis-entrypoint.sh"]
    volumes:
      - ./slave-1/data:/data
      - ./redis-slave-1.conf:/usr/local/etc/redis/redis.conf
      - ./redis-entrypoint.sh:/redis-entrypoint.sh:ro
    ports:
      - "6382:6379"
      - "16382:16379"
    restart: always
    deploy:
      resources:
        limits:
          cpus: "0.3"
          memory: "32M"
        reservations:
          cpus: "0.15"
          memory: "16M"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
  ...

  redis-exporter:
    container_name: redis-exporter
    image: oliver006/redis_exporter:latest
    ports:
      - "9121:9121"
    restart: unless-stopped
    environment:
      - REDIS_ADDR=redis://redis-master-1:6379
      - REDIS_EXPORTER_IS_CLUSTER=true
    depends_on:
      - redis-master-1
      - redis-master-2
      - redis-master-3
      - redis-slave-1
      - redis-slave-2
      - redis-slave-3
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: '256M'
        reservations:
          cpus: '0.5'
          memory: '128M'
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Redis Config ⚙️

在 Docker 的配置中，我們覆寫了 CMD 的默認啟動命令，改為使用自定義的 entrypoint 腳本 `/redis-entrypoint.sh`，並通過掛載的配置文件來啟動 Redis。

### redis-entrypoint.sh 📌

啟動命令腳本，很簡單只需要執行 Redis 並指定配置文件即可。

```bash
#!/bin/bash
set -e
exec redis-server /usr/local/etc/redis/redis.conf
```

### redis.conf 📌

Redis 的配置文件，這裡可以根據需求修改各種配置選項。這裡配置了常用的配置選項，重要的是集群模式相關的配置。

```conf
bind 0.0.0.0
port 6379
protected-mode no

# 给容器内部日誌/數據的默認路徑
loglevel notice
dir /data

# RDB 快照配置
save ""

# AOF 持久化
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# AOF 重寫配置
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# 啟用集群模式
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
# 告訴其他節點本節點的 IP 和端口信息
cluster-announce-ip 127.0.0.1
cluster-announce-port 6379
cluster-announce-bus-port 16379
```

### redis-cluster-create.sh 📌

部署 Redis 集群時，除了使用 Docker Compose 創建 Redis 節點，還需要使用 `redis-cli` 指令將建立好的各個節點組成集群。會使用到 `redis-cli --cluster create` 命令，並指定所有節點的 IP 和端口。在自動化部署中，我們也可以預先寫好一個腳本來自動執行這些命令，方便快速部署整個集群。

```bash
#!/bin/bash
set -e

# 創建 Redis 集群
redis-cli --cluster create \
  127.0.0.1:6379 \
  127.0.0.1:6380 \
  127.0.0.1:6381 \
  127.0.0.1:6382 \
  127.0.0.1:6383 \
  127.0.0.1:6384 \
  --cluster-replicas 1
```

如此一來，Redis 集群就成功創建完成了。

## 監控 📊

接著，我們可以使用 Redis Exporter 來監控 Redis 集群的運行狀態。Redis Exporter 會將 Redis 的各種指標暴露給 Prometheus，從而實現對 Redis 集群的監控。

在 Prometheus 的配置中，我們需要添加一些配置，指向 Redis Exporter 暴露的指標端點。例如:

```yaml
scrape_configs:
  - job_name: 'redis-cluster'
    http_sd_configs:
      - urls: "http://redis-exporter:9121/discover_cluster_nodes"
      refresh_interval: 30s
    metrics_path: /scrape
    relabel_configs:
      - target_label: type
        replacement: redis_cluster
```

這種方式可以讓 Prometheus 透過一個統一的 Redis Exporter 端點來監控整個 Redis 集群，不需要為了每個 Redis 節點單獨配置監控。又可以動態發現集群中的新節點。

![Redis Cluster Monitoring](/img/posts/db/redis-cluster/singlenode/monitor-example.png "Redis Cluster 監控面板範例")
