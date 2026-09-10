---
title: "Redis Cluster 節點管理：新增、移除與 Slot 重新分配"
date: 2026-09-10T08:53:03+08:00
draft: true
description: ""
---

## 前言🔖

當我們建立好 Redis Cluster 之後，久而有之，可能會因為業務需求變化，需要新增或移除節點。此時想要在不停機的情況下進行節點管理，就需要了解 Redis Cluster 的節點管理機制，包括新增節點、移除節點以及 Slot 的重新分配。

## 新增節點➕

如果要在 Redis Cluster 中新增節點，首先需要準備好新的 Redis 節點，將一部分的 Slot 和數據分配給新的節點。

新節點的資訊如下：

- IP: 192.168.1.104
- Port: 6379
- IP: 192.168.1.104
- Port: 6380

這裡會需要將 6379 的 Redis 加入 Master 節點。6380 的 Redis 作為 Slave 節點。

需要執行的步驟：

1. 在現有的 Redis Cluster 的任意節點使用 CLUSTER MEET 命令將新的節點加入集群。

    ```shell
    redis-cli -h $redis_cluster_host -p 6379 CLUSTER MEET 192.168.1.104 6379
    redis-cli -h $redis_cluster_host -p 6379 CLUSTER MEET 192.168.1.104 6380
    ```

    新舊節點通訊一段時間以後，可以使用 CLUSTER NODES 命令查看集群中的節點資訊，確認新節點是否已成功加入。

    ```shell
    redis-cli -h $redis_cluster_host -p 6379 CLUSTER NODES
    ```

    此時，如果看到了新加入的節點資訊會發現新節點兩個都是 Master。

2. 使用 CLUSTER REPLICATE 命令將新的 Slave 節點設置為對應的 Master 節點的從節點。

    ```shell
    # 先獲取 Master 節點的 ID
    master_node_id=$(redis-cli -h 192.168.1.104 -p 6379 CLUSTER NODES | grep myself | awk '{print $1}')
    redis-cli -h 192.168.1.104 -p 6380 CLUSTER REPLICATE $master_node_id
    ```

3. 使用 CLUSTER ADDSLOTS 命令將新的 Master 節點分配到相應的 Slot。
    一開始有三個 Master 節點每個節點負責 5461 個 Slot：

     - M1（0-5460）
     - M2（5461-10921）
     - M3（10922-16383）

    新增的 Master 節點需要從現有的 Master 節點那裡分配一些 Slot 過來，16383 除以 4 大約是 4095，4095 再除以 3 大約是 1365，每個現有的 Master 節點需要分配 1365 個 Slot 給新的 Master 節點。

     - M1（0-4094）
     - M2（5461-9556）
     - M3（10922-15018）
     - M4（4095-5460、9557-10921、15019-16383）

    ```shell
    redis-cli --cluster reshard 192.168.1.104:6379 --cluster-from <source_node_id> --cluster-to <target_node_id> --cluster-slots <number_of_slots> --cluster-yes
    ```

4. 使用 CLUSTER INFO 命令檢查集群狀態，確保新的節點已成功加入並分配了 Slot。

    ```shell
    redis-cli -h $redis_cluster_host -p 6379 CLUSTER INFO
    ```