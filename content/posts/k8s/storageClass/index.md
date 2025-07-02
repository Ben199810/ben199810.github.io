---
title: "StorageClass"
date: 2025-07-01T17:18:42+08:00
draft: false
tags: ["Kubernetes", "K8s", "Storage"]
description: ""
---

## 介紹

每個 StorageClass 都包含 `provisioner`、`parameters`、`reclaimPolicy` 這些字段會在 StorageClass 需要動態配置 PersistentVolume 以滿足 PersistentVolumeClaim (PVC) 使用到。

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: low-latency
provisioner: csi-driver.example-vendor.example
reclaimPolicy: Retain # 默认值是 Delete
allowVolumeExpansion: true
mountOptions:
  - discard # 这可能会在块存储层启用 UNMAP/TRIM
volumeBindingMode: WaitForFirstConsumer
parameters:
  guaranteedReadWriteLatency: "true" # 这是服务提供商特定的
```

## 磁碟區插件

每個 StorageClass 都會有 `provisioner` ，用來決定使用哪個磁碟區插件。(必要)

| 卷插件 | 內置製備器 | 配置範例 |
| --- | --- | --- |
| AzureFile | ✓ | [Azure File](https://kubernetes.io/zh-cn/docs/concepts/storage/storage-classes/#azure-file) |
| CephFS | - | - |
| FC | - | - |
| FlexVolume | - | - |
| iSCSI | - | - |
| Local | - | [Local](https://kubernetes.io/zh-cn/docs/concepts/storage/storage-classes/#local) |
| NFS | - | [NFS](https://kubernetes.io/zh-cn/docs/concepts/storage/storage-classes/#nfs) |
| PortworxVolume | ✓ | [Portworx Volume](https://kubernetes.io/zh-cn/docs/concepts/storage/storage-classes/#portworx-volume) |
| RBD | ✓ | [Ceph RBD](https://kubernetes.io/zh-cn/docs/concepts/storage/storage-classes/#ceph-rbd) |
| VsphereVolume | ✓ | [vSphere](https://kubernetes.io/zh-cn/docs/concepts/storage/storage-classes/#vsphere) |

## 回收策略

StorageClass 動態建立的 PersistentVolume 會在 `reclaimPolicy` 指定回收策略，可以是 `Delete` 或 `Retain` 。預設是 `Delete` 。

## 擴展

PersistentVolume 可以配置為可擴充，允許透過 PVC 物件來調整磁碟區大小，申請一個新的、更大的儲存容量。當 `allowVolumeExpansion` 定義為 true 時，下列類型的磁碟區支援擴充。

| 卷類型 | 卷擴展的Kubernetes 版本要求 |
| --- | --- |
| Azure File | 1.11 |
| CSI | 1.24 |
| FlexVolume | 1.13 |
| Portworx | 1.11 |
| rbd | 1.11 |

## 掛載選項

由 StorageClass 動態建立的 PersistentVolume 將使用類別中 `mountOptions`指定的掛載選項。

如果磁碟區插件不支援掛載選項，卻指定了掛載選項，則製備操作會失敗。 掛載選項在 StorageClass 和 PV 上都**不會**做驗證。如果其中一個掛載選項無效，那麼這個PV 掛載作業就會失敗。

## 參考

[動態卷製備](https://kubernetes.io/zh-cn/docs/concepts/storage/dynamic-provisioning/)
