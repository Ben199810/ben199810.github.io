---
title: "Datadog Stopped Collecting Kafka Metrics"
date: 2025-07-18T12:20:37+08:00
draft: true
tags: ["Datadog", "Kafka", "Metrics"]
description: ""
---
## 事件過程

近期有公司同仁反應 Datadog 停止收集 Kafka 的 metrics，因此進行調查的過程紀錄下來。未來若有同樣的問題，可以參考這篇文章。

## 架構圖

先來了解 Kafka Metrics 是如何被 Datadog 收集的。

datadog agent 會部署在 Kubernetes 環境中，且在 node 中運行。它會收集 Pod 服務的 metrics，也會收集 Kafka 的 metrics。

要注意的是 Kafka 的 VM 並沒有部署 Datadog Agent，而是透過 Kubernetes 的 Datadog Agent 來收集 Kafka 的 metrics。

這麼做的原因是 Datadog Agent 收費是會依照使用的 Agent 數量計算的，可以減少費用的產生。

<div style="background-color:white; padding: 20px">
{{< mermaid >}}
flowchart LR
  subgraph kubernetes
    subgraph node
      datadog[Datadog Agent]
      pod[Pod]
    end
  end

  subgraph GCE
    kafka[Kafka]
  end

  datadog -->|收集| kafka
  datadog -->|收集| pod
{{</ mermaid >}}
</div>

## 問題調查

1. 確認網路連線是否異常

    首先確認 Datadog Agent 是否能夠連線到 Kafka 的 metrics endpoint。要怎麼確認 kafka 的 metrics endpoint 是什麼呢？

    可以在 Kafka 的配置檔中找到，在配置監控系統時，如果採用 JMX Exporter 的方式，則可以在 /etc/systemd/system/kafka.service 中找到。

    `-Dcom.sun.management.jmxremote.port` 這個參數指定了 JVM 的 JMX 監控端口，通常是 9134。

    `-Dcom.sun.management.jmxremote.rmi.port` 這個參數指定了 RMI (遠端方法呼叫) 的端口。預設情況下，JMX 會動態選擇一個 RMI 端口，在雲端或防火牆環境下，動態端口會導致難以開放防火牆規則。

    將 jmxremote.port 和 jmxremote.rmi.port 設定相同，可確保 JMX 監控只啟用此連接埠（此處為 9134）例，防火牆設定和安全監控管。

    ```toml
    [Service]
    Environment="KAFKA_JMX_OPTS=-Dcom.sun.management.jmxremote=true -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.port=9134 -Djava.rmi.server.hostname=10.106.10.151"
    ```

2. 檢查 VM 監控端口是否開啟

    ```bash
    netstat -an | grep 9134
    # 或
    lsof -i :9134
    ```

3. 檢查 Kubernetes 到 Kafka 的連線是否異常

    在 Kubernetes 環境中，建立一個 Pod，並使用 curl 或 telnet 測試連線到 Kafka 的 JMX 端口。

    ```yaml
    apiVersion: v1
    kind: Pod
    metadata:
      name: test-kafka-JMX-connection
    spec:
      containers:
      - name: test-container
        image: maven:3.8-openjdk-11
        command:
          - /bin/sh
          - -c
        args:
          - |
            echo "Downloading jmxterm..."
            curl -L -s -o /tmp/jmxterm.jar https://github.com/jiaqi/jmxterm/releases/download/v1.0.2/jmxterm-1.0.2-uber.jar;
            echo "Testing JMX connection to Kafka..."
            get -b kafka.server:type=KafkaServer,name=BrokerState Value | java -jar /tmp/jmxterm.jar -n -l ${KAFKA_JMX_HOST}:9134;
            echo "JMX connection test completed."
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
    ```

4. 確認 Datadog Agent 的配置

    確認 Datadog Agent 的配置檔中是否有正確設定 Kafka 的 JMX 端口。通常在 `/etc/datadog-agent/conf.d/kafka.d/conf.yaml` 中。

    ```yaml
    init_config: {}
    instances:
      - host: <kafka-host>
        port: 9134
        tags:
          - kafka
    ```

## 參考資料

[聊聊 Kafka 如何基於 JMX 監控](https://juejin.cn/post/7278918966214721547)
