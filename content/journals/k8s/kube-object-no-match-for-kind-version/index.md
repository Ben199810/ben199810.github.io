---
title: "Kube Object No Match for Kind Version"
date: 2025-07-02T14:23:37+08:00
draft: false
tags: ["k8s", "helm", "mapkubeapis", "autoscaling"]
description: "解決 Helm 升級時遇到的 Kubernetes API 版本不匹配問題"
---
最近在升級 helm release 時遇到了一個錯誤，提示 "no matches for kind HorizontalPodAutoscaler in version autoscaling/v2beta2"。

原因是因為 Kubernetes 的 API 版本變更，導致舊的資源定義不再匹配新的 API 版本。

![Kube Object No Match for Kind Version](/img/k8s/kube-object-no-match-for-kind-version.png)

## 解決方法

因為是正式站環境的 log 服務，log 的收集對 RD 在排查問題時非常重要。如果刪除後再重新部署，會導致 log 的丟失。

Helm3 支援一款插件工具 `mapkubeapis`，可以將有使用已棄用或已刪除的 API 的 Helm Release metadata 更新為有受支援的 API。

```bash
helm mapkubeapis -n kube_namespace releaseName
```

![helm mapkubeapis update kube object api version](/img/k8s/helm-mapkubeapis-update-kube-object-api-version.png)

## 參考資料

[Helm upgrade failure due to deprecated or removed Kubernetes API](https://faun.pub/helm-upgrade-failure-due-to-deprecated-or-removed-kubernetes-api-3c5e56b634d7)
