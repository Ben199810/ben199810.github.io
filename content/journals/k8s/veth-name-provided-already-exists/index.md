---
title: "container veth name provided (eth0) already exists 故障排除"
date: 2023-09-17
draft: false
description: "紀錄在工作時踩的坑，關於 CNI 底層"
tags: ["k8s", "pod", "node", "cni"]

---
## 前言
最近在協助公司專案轉雲端架構時，由於服務只能啟用一個 pod 提供線上服務的運作，因此也選擇使用 `statefulSet` 部署服務，在這過程中發現的問題。

## 事件流程
RD 同仁更新了 code 到 gitLab，並沒有順利的完成 CICD。原因是 statefulSet pod 在關閉時，停留在 `terminating`，雖然 k8s 有 `terminationGracePeriodSeconds`，但由於情況特殊。當下的 terminationGracePeriodSeconds 是 14400，長達四小時。

因線上緊急的問題，所以針對 terminating pod 採取了 `kubectl delete pod [pod name] --grace-period=0 --force`。之後重新建立的 pod 就會出現以下的錯誤訊息 :backhand_index_pointing_down:

{{< alert icon="fire" cardColor="#e63946" iconColor="#1d3557" textColor="#f1faee" >}}
container veth name provided (eth0) already exists
{{< /alert >}}

## Google Support
其實前陣子已經有錯誤影響到開發跟測試環境了，由於這次影響到正式環境。把案件單等級提升至 P1 並請 google 協助查找錯誤發生的原因。

這次會發生的上述錯誤的原因，經過 google 協助主要是推測在 pod 進入關閉流程時，由於 `terminationGracePeriodSeconds` 設置時長有四小時，尚處於 pod 的 lifecycle 這時候，使用 `kubectl delete pod --force` 會導致隨然 pod 消失了，但有 container 設定殘留在 node 上，如果此時新的 pod 重新在同一顆 node 上面啟動就會造成有相同設定。

雖然改成 deployment 可以規避，但相對的會浪費一組 IP，長久下來一樣會有問題。最重要的還是要讓 pod 結束整個 lifecycle 才不會產生後續的問題。