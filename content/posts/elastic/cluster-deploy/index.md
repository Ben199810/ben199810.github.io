---
title: "Cluster Deploy"
date: 2026-04-20T09:09:58+08:00
draft: true
description: ""
---

## 前言🔖

elasticsearch 對於可觀測性來說是非常重要的，尤其是在分散式系統中。它可以幫助我們收集、分析和可視化來自不同來源的數據，從而更好地理解系統的運行狀況和性能。

以下範例會使用 docker-compose 來部署一個簡單的 elasticsearch 集群，包含三個節點。
使用的 elasticsearch 版本為 8.9.2，kibana 版本為 8.9.2。

## 部署步驟🚀

首先，我們需要創建一個 `docker-compose.yml` 文件，內容如下：

```yaml
services:
  es01:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.9.2
    container_name: es01
    restart: unless-stopped
    environment:
      - node.name=es01
      - cluster.name=es-docker-cluster
      - discovery.seed_hosts=es02,es03
      - cluster.initial_master_nodes=es01,es02,es03
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms8g -Xmx8g"
      - "xpack.security.enabled=false"
      - "indices.memory.index_buffer_size=30%"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - /database/esdata1:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          cpus: "8"
          memory: 16G
        reservations:
          cpus: "3"
          memory: 8G
    networks:
      - elk
  es02:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.9.2
    container_name: es02
    restart: unless-stopped
    environment:
      - node.name=es02
      - cluster.name=es-docker-cluster
      - discovery.seed_hosts=es01,es03
      - cluster.initial_master_nodes=es01,es02,es03
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms8g -Xmx8g"
      - "xpack.security.enabled=false"
      - "indices.memory.index_buffer_size=30%"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - /database/esdata2:/usr/share/elasticsearch/data
    ports:
      - "9201:9200"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          cpus: "8"
          memory: 16G
        reservations:
          cpus: "3"
          memory: 8G
    networks:
      - elk
  es03:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.9.2
    container_name: es03
    restart: unless-stopped
    environment:
      - node.name=es03
      - cluster.name=es-docker-cluster
      - discovery.seed_hosts=es01,es02
      - cluster.initial_master_nodes=es01,es02,es03
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms8g -Xmx8g"
      - "xpack.security.enabled=false"
      - "indices.memory.index_buffer_size=30%"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - /database/esdata3:/usr/share/elasticsearch/data
    ports:
      - "9202:9200"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          cpus: "8"
          memory: 16G
        reservations:
          cpus: "3"
          memory: 8G
    networks:
      - elk
  kibana:
    image: docker.elastic.co/kibana/kibana:8.9.2
    container_name: kibana
    restart: unless-stopped
    environment:
      - ELASTICSEARCH_HOSTS=["http://es01:9200","http://es02:9200","http://es03:9200"]
      - SERVER_HOST=0.0.0.0
      - SERVER_NAME=kibana
    ports:
      - "5601:5601"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 2G
        reservations:
          cpus: "1"
          memory: 1G
    depends_on:
      - es01
      - es02
      - es03
    networks:
      - elk

networks:
  elk:
    driver: bridge
```

接著，說明一下這個 `docker-compose.yml` 需要注意的細節以及內容：

1. **服務定義**：我們定義了四個服務：`es01`、`es02`、`es03` 和 `kibana`。前三個是 Elasticsearch 節點，最後一個是 Kibana。
2. **環境變量**：每個 Elasticsearch 節點都設置了必要的環境變量，如 `node.name`、`cluster.name`、`discovery.seed_hosts` 和 `cluster.initial_master_nodes`，這些變量確保了節點之間的通信和集群的正確組建。
3. **資源限制**：我們為每個服務設置了 CPU 和內存的限制和預留，以確保它們在運行時有足夠的資源。
4. **數據持久化**：每個 Elasticsearch 節點都將數據存儲在主機的 `/database/esdataX` 目錄中，這樣即使容器重啟，數據也不會丟失。
5. **網絡配置**：我們使用了一個名為 `elk` 的自定義橋接網絡，這樣服務之間可以通過服務名稱互相通信。

補充說明：

- `bootstrap.memory_lock=true`：這個設置允許 Elasticsearch 鎖定內存，防止它被交換到磁盤上，這對於性能非常重要。
如何驗證記憶體鎖定是否成功：

```text
GET _nodes?filter_path=**.mlockall
```

如果返回 `true`，則表示記憶體鎖定成功。

- `ES_JAVA_OPTS=-Xms8g -Xmx8g`：這個設置指定了 Elasticsearch 的 Java 堆內存大小，建議設置為物理內存的一半，但不超過 32GB。
- `xpack.security.enabled=false`：這個設置禁用了 Elasticsearch 的安全功能，這樣我們就不需要設置用戶名和密碼來訪問 Elasticsearch。
- `indices.memory.index_buffer_size=30%`：這個設置指定了 Elasticsearch 用於索引緩衝區的內存大小，預設為 10%，因為日誌量較大，所以我們將其增加到 30%。建議根據實際情況調整這個值。
- `logging`：我們使用了 `json-file` 日誌驅動程序，並設置了日誌文件的最大大小和數量，以防止日誌文件過大。
