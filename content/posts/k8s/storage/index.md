---
title: "PersistentVolume"
date: 2025-07-02T10:36:44+08:00
draft: false
tags: ["Kubernetes", "K8s", "Storage"]
description: ""
---
## 介紹

PersistentVolume (PV) 是 Kubernetes 中的一種資源，用於提供持久化存儲。它是集群級別的存儲資源，與 Pod 的生命週期無關。PV 可以被多個 Pod 共享，並且可以在 Pod 重啟或重新調度時保持數據不變。

管理員可以事先創建 PV，並將其與特定的存儲系統（如 NFS、iSCSI、雲存儲等）綁定，或使用動態存儲類別（StorageClass）來自動創建 PV。

PersistentVolumeClaim (PVC) 是用戶請求存儲的方式。概念與 Pod 請求資源類似。用戶可以創建 PVC，指定所需的存儲大小和存取模式 (如 ReadWriteOnce、ReadOnlyMany 等)。Kubernetes 會根據 PVC 的要求來匹配合適的 PV。

## 存取模式

- ReadWriteOnce (RWO)：卷只能被單個節點以讀寫方式掛載。
- ReadOnlyMany (ROX)：卷可以被多個節點以只讀方式掛載。
- ReadWriteMany (RWX)：卷可以被多個節點以讀寫方式掛載。

## PersistentVolume 與 PersistentVolumeClaim

<div style="background-color:white; padding: 20px">
{{< mermaid >}}
graph

pod(Pod)
volume(Volume)
PVC(PersistentVolumeClaim)
PV(PersistentVolume)
storageClass(StorageClass)
storageProvider(StorageProvider)
storage(Physical Storage)

pod -->|使用| volume --> PVC
PVC -->|靜態綁定| PV
PVC -->|動態綁定| storageClass

PV -->|提供存儲| storage
storageClass -->|配置存儲| storageProvider -->|實際存儲| storage
{{< /mermaid >}}
</div>

如果 PVC storageClassName 屬性為 `""`，則表示使用靜態綁定。這意味著 PVC 自身禁止使用動態製備的卷。

## 參考

[[Kubernetes / K8s] PV/ PVC 儲存大小事交給PV/PVC管理](https://medium.com/k8s%E7%AD%86%E8%A8%98/kubernetes-k8s-pv-pvc-%E5%84%B2%E5%AD%98%E5%A4%A7%E5%B0%8F%E4%BA%8B%E4%BA%A4%E7%B5%A6pv-pvc%E7%AE%A1%E7%90%86-4d412b8bafb5)

[持久卷](https://kubernetes.io/zh-cn/docs/concepts/storage/persistent-volumes/)
