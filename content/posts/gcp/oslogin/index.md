---
title: "使用 OS Login 管理 GCP VM 存取權"
date: 2025-12-22T15:57:06+08:00
draft: false
description: ""
tags: ["gcp","oslogin"]
---
## 前言🔖

近期在接管公司 GCP 專案，發現 IT 團隊以前使用 OS Login 來管理 VM 的存取權限，因為之前沒有使用過這個功能，所以特別研究了一下 OS Login 的設定方式，並將設定過程記錄在此篇文章中。

## 什麼是 OS Login？🤔

什麼是 OS Login？ OS Login 跟一般傳統的 SSH 金鑰管理方式有什麼不同？相較之下有哪些優點？接著往下看就知道了！

OS Login 是 Google Cloud Platform (GCP) 提供的一種身份驗證和授權機制，允許使用者使用其 Google 帳戶來存取和管理 GCP 上的虛擬機器 (VM)。透過 OS Login，使用者可以將其 IAM 角色與 VM 的存取權限綁定，從而實現更細緻的權限控制。

## 架構🏗️

這邊有一個簡單的架構圖說明公司內部管理 VM 存取的方式：

使用者可以透過 SSH IAP 連線到堡壘機 (Bastion Host)，但是不能夠直接連線到其他的 VM。堡壘機會使用 OS Login 來驗證使用者的身份，並根據 IAM 角色來決定使用者是否有權限存取其他的 VM。

<div style="background-color:white; padding: 20px">
{{< mermaid >}}

graph LR
    user[使用者] -- SSH IAP --> bastion[堡壘機]
    bastion -- OS Login --> jenkins[Jenkins]
    bastion -- OS Login --> appserver[App Server]
    bastion -- OS Login --> dbserver[DB Server]

{{< /mermaid >}}
</div>

## OS Login 的優點🌟

如果使用傳統的 SSH 金鑰管理方式，通常需要在每台 VM 上面設定使用者的公鑰，當使用者需要存取 VM 時，就會使用對應的私鑰來進行驗證。但是這種方式在管理上會比較麻煩，尤其是當使用者數量增加或是 VM 數量增加時，維護公鑰的工作量會變得很大。

OS Login 則是將使用者的存取權限與 IAM 角色綁定，當使用者需要存取 VM 時，系統會根據 IAM 角色來決定使用者是否有權限存取該 VM。這樣的好處是可以集中管理使用者的存取權限，並且可以透過 IAM 來設定更細緻的權限控制。

## OS Login 的設定步驟🛠

首先需要建置一台堡壘機 (Bastion Host)，因為堡壘機需要能夠存取其他的 VM，所以需要設定 IAM 權限，以及 SCOPES。

1. 建立一個獨立的 Service Account 提供堡壘機使用，並且賦予以下的 IAM 角色，以便讓堡壘機能夠使用 OS Login 功能：
    - roles/compute.osLogin
    - roles/compute.osAdminLogin (如果需要管理員權限)
    - roles/iam.serviceAccountUser
    - roles/compute.viewer
    ![IAM 角色設定範例](/img/oslogin/sa-roles.png "IAM 角色設定範例")
2. 在建立堡壘機的時候，設定 SCOPES，確保包含以下的 SCOPES：
    - cloud-platform

  補充說明：什麼是 SCOPES❓
    SCOPES 是 GCP 中用來定義 VM 可以存取哪些 API 的權限範圍。當 VM 需要存取某些 GCP 服務時，必須先設定相應的 SCOPES，才能夠成功存取這些服務。上述的範例中，cloud-platform SCOPES 代表 VM 可以存取所有的 GCP 服務。在 GCP 控制台畫面可以看到 VM 的設定會如下圖所示：
    ![VM SCOPES 設定範例](/img/oslogin/cloud-platform-scope.png "VM SCOPES 設定範例")

做完上面兩個步驟之後，就有一台可以使用 OS Login 功能的堡壘機了。接著建立公司內部使用的其他 VM，例如： Jenkins、App Server、DB Server 等等，這些 VM 需要這定開啟 OS Login 功能。這樣的話，當使用者透過堡壘機連線到這些 VM 時，就會使用 OS Login 來進行身份驗證。

1. 建立其他內部 VM 時，確保在 VM 的 Metadata 中設定 `enable-oslogin` 為 `TRUE`，這樣才能啟用 OS Login 功能。
    ![VM Metadata 設定範例](/img/oslogin/vm-metadata.png "VM Metadata 設定範例")

## 驗證✅

1. 首先我們可以檢查堡壘機的設定是不是正確的：

    ```bash
    # 在本地電腦執行，查詢跳板機的 Service Account
    gcloud compute instances describe bastion-vm \
        --zone=ZONE \
        --format="get(serviceAccounts[0].email)"

    # 查詢 scopes
    gcloud compute instances describe bastion-vm \
        --zone=asia-east1-b \
        --format="get(serviceAccounts[0].scopes[])"
    ```

2. 接著檢查 service account 的 IAM 角色是否正確：

    ```bash
    gcloud projects get-iam-policy PROJECT_ID --flatten="bindings[].members" --format="value(bindings.role)" --filter="bindings.members:BASTION_SERVICE_ACCOUNT_EMAIL"
    ```

3. 進入堡壘機，測試連線

    ```bash
    # 使用 gcloud compute ssh 連線到堡壘機
    gcloud compute ssh bastion-vm --zone=ZONE

    # 在跳板機內，查詢 Service Account 的 OS Login 使用者名稱
    gcloud compute os-login describe-profile
    ```

4. 檢查內部 VM 的設定是否正確：

    ```bash
    # 檢查 Jenkins VM 是否啟用 OS Login
    gcloud compute instances describe p-vp-jenkins \
      --zone=asia-east1-b \
      --format="get(metadata.items[]. value)" \
      --flatten="metadata.items[]" \
      | grep -i oslogin
    ```

## 總結📝

上述的步驟完成之後，就可以使用 OS Login 來管理 GCP VM 的存取權限了。公司內部的個人帳號沒有 OS Login 權限，所以無法直接連線到 VM，只能透過堡壘機來進行存取，這樣可以提高整體的安全性。也避免了傳統 SSH 金鑰管理方式的繁瑣，讓權限管理更加集中和方便。

## 參考文獻📚

[Google Cloud | 設定 OS 登入](https://docs.cloud.google.com/compute/docs/oslogin/set-up-oslogin?hl=zh-tw)
