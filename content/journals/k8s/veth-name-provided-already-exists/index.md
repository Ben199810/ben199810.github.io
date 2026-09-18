---
title: "解決 Kubernetes Pod 網路衝突：container veth name provided (eth0) already exists"
date: 2023-09-17
draft: false
description: "記錄在使用 StatefulSet 部署時遇到的 Pod 網路介面衝突問題，以及如何透過正確的 Pod 生命週期管理來解決此問題"
tags: ["Kubernetes", "CNI"]
---

## 前言

最近公司專案轉雲端架構時，由於服務只能啟用一個 pod 提供線上服務的運作，因此也選擇使用 `statefulSet` 部署服務，在這過程中發現的問題。

## 事件流程

RD 同仁更新了 code 到 gitLab，但沒有順利完成 CICD。原因是 StatefulSet pod 在關閉時停留在 `terminating` 狀態。雖然 k8s 有 `terminationGracePeriodSeconds` 設定，但由於情況特殊，當下的 terminationGracePeriodSeconds 設為 14400 秒，長達四小時。

因為線上緊急問題，所以針對 terminating pod 採取了強制刪除：`kubectl delete pod [pod name] --grace-period=0 --force`。之後重新建立的 pod 就會出現以下錯誤訊息 👇

```log
Warning
(combined from similar events): Failed to create pod sandbox: rpo error: code = Unknown desc = failed to setup network for sandbox
"14fe0cd3d688aed4ffed4c36ffab1a145230449881bcbe4cac6478a63412b0c*: plugin type=*gke" failed (add): container veth name provided (etho) already exists
```

## Google Support

其實前陣子這個錯誤已經影響到開發和測試環境了。由於這次影響到正式環境，我們把案件等級提升至 P1，並請 Google 協助查找錯誤發生的原因。

經過 Google 協助分析，這次錯誤的主要原因如下：

- 當 pod 進入關閉流程時，由於 `terminationGracePeriodSeconds` 設置為四小時，pod 仍處於 lifecycle 中
- 此時使用 `kubectl delete pod --force` 會導致 pod 雖然消失，但 container 設定仍殘留在 node 上
- 如果新的 pod 重新在同一顆 node 上啟動，就會造成相同的網路介面設定衝突

雖然改成 Deployment 可以規避此問題，但相對會浪費一組 IP。長久下來一樣會有問題，最重要的還是要讓 pod 完整結束整個 lifecycle，才不會產生後續問題。

## 技術細節補充

Container Network Interface (CNI) 在 Kubernetes 中負責管理 Pod 的網路設定。當 Pod 啟動時，CNI 會為其創建一個虛擬網路介面 (veth pair)，並將其連接到 Pod 的網路命名空間。

## 參考資料

[Pods stuck on ContainerCreating after containerd is restarted](https://github.com/containerd/containerd/issues/7010)
