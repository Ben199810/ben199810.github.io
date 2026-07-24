---
title: "使用 OS Login 管理 GCP VM"
date: 2025-12-22T15:57:06+08:00
draft: false
description: ""
tags: ["GCP", "OS Login"]
---

## 前言🔖

傳統開發過程中，開發者需要透過 SSH 登入虛擬主機。IT 運維人員需要管理大量的 SSH 公開金鑰，當組織或者部門有異動時，很多 SSH 金鑰的許可權會變的難以追蹤，大量的導致運維人員需要花費大量的時間去管理 SSH 金鑰，這樣的方式不僅效率低下，也容易出現安全漏洞。

透過 GCP 的 OS Login 功能，可以減少 SSH 金鑰管理的複雜度，使用 IAM 角色管理使用者的存取權限。不必需要在每台 VM 上面設定使用者的公鑰。

## google 網路論壇🗣️

google 網路論壇可以新增群組，並且可以將群組與 IAM 角色綁定，這樣就可以透過群組來管理使用者的存取權限。當使用者需要存取 VM 時，系統會根據 IAM 角色來決定使用者是否有權限存取該 VM。

![google 網路論壇設定範例](/img/posts/gcp/oslogin/google-group.png "google 網路論壇設定範例")

將群組的 Email 加入到身份與存取權管理中，授予 `compute.osLogin`、`iam.serviceAccountUser`、`iap.tunnelResourceAccessor` 角色。如果需要管理員權限，可以將 `compute.osLogin` 角色改為 `compute.osAdminLogin`。

## GCE Metadata 設定⚙️

GCE 開啟 OS Login 功能需要在 VM 的 Metadata 中設定 `enable-oslogin` 為 `TRUE`，這樣才能啟用 OS Login 功能。如果管理的 VM 數量很多，建議可以在專案層級 Compute Engine > 設定 > 中繼資料中設定。如此一來，所有 VM 都會繼承這個設定，避免每台 VM 都需要手動設定。

![VM Metadata 設定範例](/img/posts/gcp/oslogin/vm-metadata.png "VM Metadata 設定範例")

IAM 與 Metadata 設定完成之後，在網路論壇群組中的使用者就可以透過 OS Login 來存取 GCE VM。所以可以特定的群組來管理。例如: SRE/IT 運維團隊、開發團隊、測試團隊等等。

{{< mermaid >}}

flowchart TD
subgraph maintainer[sre-mail.example.com]
sreA[運維人員 A]
sreB[運維人員 B]
end

subgraph developer[dev-mail.example.com]
devA[開發人員 A]
devB[開發人員 B]
end

subgraph IAM[身分與存取權管理]
srePermissions[compute.osAdminLogin、 iam.serviceAccountUser、iap.tunnelResourceAccessor]
devPermissions[compute.osLogin、 iam.serviceAccountUser、iap.tunnelResourceAccessor]
end

maintainer <--> srePermissions
developer <--> devPermissions

{{< /mermaid >}}

## 使用堡壘機管理🛡️

如果公司內部只有少部分的人員需要存取，也不需要特別使用群組進行管理，可以用堡壘機的方式來管理內部 VM 的存取權限。

將堡壘機的 Service Account 與 IAM 角色綁定，一樣綁定 `compute.osLogin`、`iam.serviceAccountUser`、`iap.tunnelResourceAccessor` 角色。運維團隊可以管理堡壘機的存取權限即可，受予特定的使用者可以登入堡壘機，透過堡壘機來存取內部的 VM。專注於管理堡壘機的存取權限即可！

{{< mermaid >}}
flowchart LR
bastion[堡壘機]
internalVM[內部 VM]
userA[使用者 A]

userA -->|SSH| bastion -->|OS Login| internalVM
userA -->|拒絕連線| internalVM
{{< /mermaid >}}

## 遇到的問題❓

堡壘機存取內部 VM 時，出現無法存取的錯誤訊息，檢查堡壘機的 Service Account 是否有綁定 `compute.osLogin`、`iam.serviceAccountUser`、`iap.tunnelResourceAccessor` 角色，並且確認內部 VM 的 Metadata 中是否有設定 `enable-oslogin` 為 `TRUE`。

確保堡壘機的 Cloud API 存取權範圍 (SCOPES) 包含 `cloud-platform`，這樣堡壘機才能夠存取內部 VM。

![VM SCOPES 設定範例](/img/posts/gcp/oslogin/cloud-platform-scope.png "VM SCOPES 設定範例")

## 檢查與驗證🔍

1. 檢查堡壘機的設定是否正確:

   查詢跳板機的 Service Account

   ```bash
   gcloud compute instances describe bastion-vm \
       --zone=ZONE \
       --format="get(serviceAccounts[0].email)"
   ```

   查詢 Scopes

   ```bash
   gcloud compute instances describe bastion-vm \
       --zone=asia-east1-b \
       --format="get(serviceAccounts[0].scopes[])"
   ```

2. 檢查 Service Account 的 IAM 角色是否正確:

   ```bash
   gcloud projects get-iam-policy ${PROJECT_ID} --flatten="bindings[].members" --format="value(bindings.role)" --filter="bindings.members:${BASTION_SERVICE_ACCOUNT_EMAIL}"
   ```

   ![檢查 Service Account 的 IAM 角色是否正確](/img/posts/gcp/oslogin/check-iam-role.png "檢查 Service Account 的 IAM 角色是否正確")

3. 檢查堡壘機的 OS Login 設定是否正確:

   gcloud compute ssh 連線到堡壘機

   ```bash
   gcloud compute ssh bastion-vm --zone=ZONE
   ```

   查詢 Service Account 的 OS Login 使用者名稱

   ```bash
   gcloud compute os-login describe-profile
   ```

4. 檢查內部 VM 的 Metadata 設定是否正確:

   ```bash
   gcloud compute instances describe ${INSTANCE_NAME} \
     --zone=asia-east1-b \
     --format="get(metadata.items[]. value)" \
     --flatten="metadata.items[]" \
     | grep -i oslogin
   ```

## 參考文獻📚

[Google Cloud | 設定 OS 登入](https://docs.cloud.google.com/compute/docs/oslogin/set-up-oslogin?hl=zh-tw)
