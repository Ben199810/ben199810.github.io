---
title: "Datadog Stopped Collecting Kafka Metrics"
date: 2025-07-18T12:20:37+08:00
draft: false
tags: ["datadog", "kafka", "metrics"]
description: ""
---
## 事件過程

近期公司同仁反應 Datadog 停止收集 Kafka 的 metrics，因此進行調查的過程紀錄下來。未來若有同樣的問題，可以參考這篇文章。

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

5. Datadog Support 建議

    Support 團隊建議可以使用 `flare` 傳遞資訊到案件單上，有助於排查問題。

    在 kafka integration 中，設置 checke runner (cluster_check: true) 。因此可以 flare cluster agent 的資訊。

    ```shell
    kubectl exec -it <NAMESPACE> -it <CLUSTER_POD_NAME> -- agent flare <案件編號>
    ```

    檢查 cluster check runners。

    ```shell
    kubectl exec -n <NAMESPACE> -it <CLUSTER_POD_NAME> -- agent clusterchecks
    ```

6. Datadog Support 回饋

    在提供上述的資訊之後，Support 團隊回覆在 flare (status.log) 中發現了 kafka instance 檢查的狀態。

    ```text
    =========
    JMX Fetch
    =========

    Information
    ==================
    runtime_version : 11.0.23
    version : 0.49.1
    Initialized checks
    ==================
    kafka
    - instance_name: kafka-02
      metric_count: 346
      service_check_count: 0
      message: <no value>
      status: OK
    - instance_name: kafka-01
      metric_count: 350
      service_check_count: 0
      message: Number of returned metrics is too high for instance: kafka-01. Please read http://docs.datadoghq.com/integrations/java/ or get in touch with Datadog Support for more details. Truncating to 350 metrics.
      status: WARNING
    - instance_name: kafka-03
      metric_count: 350
      service_check_count: 0
      message: Number of returned metrics is too high for instance: kafka-03. Please read http://docs.datadoghq.com/integrations/java/ or get in touch with Datadog Support for more details. Truncating to 350 metrics.
      status: WARNING
    ```
  
    `kafka-01` 和 `kafka-03` 出現以下警告訊息：

    ```text
    Number of returned metrics is too high for instance: kafka-03. Please read http://docs.datadoghq.com/integrations/java/ or get in touch with Datadog Support for more details. Truncating to 350 metrics.
    ```

    Support 團隊建議由於傳回的指標數量太高，即高於預設值 350。因此，要解決此問題，您可以新增 `max_returned_metrics` 參數並將值設為高於 350。

## 修正範例與驗證

在 values.yaml 中我們需要新增 `max_returned_metrics` 參數，並將其值設為需要的值且大於預設值。

```yaml
clusterAgent:
  confd:
    kafka.yaml: |-
      cluster_check: true
      init_config:
        is_jmx: true
        collect_default_metrics: true
        new_gc_metrics: true
      instances:
        - host: <kafka-host>
          port: 9134
          name: kafka-01
          max_returned_metrics: 500 # 新增此行
```

然後重新部署 Datadog Agent。

使用 agent status 檢查 Kafka 的 metrics count 是否已經超過 350 且 status 從 WARNING 變為 OK。

因為 agent 有很多台，所以使用腳本的方式去找到收集 Kafka VM Metrics 的 agent。

```bash
#!/bin/bash
echo "Found pods:"
kubectl get pods -n datadog -o custom-columns=NAME:.metadata.name --no-headers | grep -v cluster

read -p "搜尋關鍵字：" SEARCH_KEYWORD

PODS=$(kubectl get pods -n datadog -o custom-columns=NAME:.metadata.name --no-headers | grep -v cluster)

IFS=$'\n' read -d '' -r -a POD_ARRAY <<< "$PODS"
for POD in "${POD_ARRAY[@]}"; do
  echo "Checking status of pod: $POD"
  
  kubectl exec -n datadog $POD -c agent -- agent status | grep "$SEARCH_KEYWORD"
  if [ $? -ne 0 ]; then
    echo "No kafka-common found in $POD"
  fi
  echo "----------------------------------------"
done

echo "Finished checking all pods."
```

找到對應的 agent 之後，使用以下指令檢查 Kafka 的 metrics count。

可以看到 kafka 的 metrics count 已經超過 350 且 status 從 WARNING 變為 OK。

```text
=========
JMX Fetch
=========

  Information
  ==================
    runtime_version : 11.0.23
    version : 0.49.1
  Initialized checks
  ==================
    kafka
    - instance_name: kafka-02
      metric_count: 346
      service_check_count: 0
      message: <no value>
      status: OK
    - instance_name: kafka-01
      metric_count: 476
      service_check_count: 0
      message: <no value>
      status: OK
    - instance_name: kafka-03
      metric_count: 443
      service_check_count: 0
      message: <no value>
      status: OK
  Failed checks
  =============
    no checks
```

## 問題反思

這次問題的根本原因是 Kafka 的 metrics 數量超過了 Datadog 的預設限制，導致部分 metrics 無法被收集。

1. 如果不提高 `max_returned_metrics` 的上限值，有方法可以降低 `metric_count` 的數量嗎？

    support 提供以下的方式減少 `metric_count` 的數量：

    metric_count 值是每個 instance 的 Datadog 指標總數。

    對於 Kafka integration，Datadog 指標是藉助此文件 metrics.yaml [（ 連結 ）](https://github.com/DataDog/integrations-core/blob/master/kafka/datadog_checks/kafka/data/metrics.yaml) 生成的，如果集成找到具有匹配的 domain、bean 和 attribute 的 jmx 指標，它將生成 Datadog 指標。

    如果您想要減少 metric_count 值，您可以將此參數變更為 `collect_default_metrics` 為 false ，這樣就不會使用 metrics.yaml ，然後建立您自己的配置以專門匹配任何 jmx 指標以從此範例[（ 連結 ）](https://github.com/DataDog/integrations-core/blob/master/kafka/datadog_checks/kafka/data/conf.yaml.example#L37)產生 Datdog 指標。

## 參考資料

[聊聊 Kafka 如何基於 JMX 監控](https://juejin.cn/post/7278918966214721547)
