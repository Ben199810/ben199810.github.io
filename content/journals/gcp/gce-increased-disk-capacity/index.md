---
title: "GCE VM 增加磁碟容量的實作步驟分享"
date: 2026-03-31T09:10:39+08:00
draft: false
tags: ["GCP", "GCE", "磁碟容量", "VM", "Google Cloud"]
description: "分享在 GCE VM 上增加磁碟容量的實作步驟，包含增加磁碟容量以及讓作業系統認識新的磁碟容量的過程。本文將介紹如何使用 gcloud CLI 或 Terraform 來增加磁碟容量，以及如何使用 df、lsblk 和 parted 等指令來確認磁碟的狀態，最後使用 xfs_growfs 或 resize2fs 指令來擴增磁碟大小。"
---
## 前言🔖

最近需要幫助 Elasticsearch 的 VM 增加磁碟容量，過程中參考了 Google Cloud 的官方文件，發現增加磁碟容量的過程其實非常簡單，主要分為兩個步驟：第一步是增加磁碟容量，第二步是讓作業系統認識新的磁碟容量。

## 實作步驟📌

### 增加磁碟容量🔍

首先第一點就是要增加磁碟容量，讀者可以使用 Google Cloud Console 的 UI 介面來增加磁碟容量，或者是使用 gcloud CLI 的方式來增加磁碟容量。

注意: 這裡的 `DISK_NAME` 、`DISK_SIZE` 和 `ZONE` 都需要替換成實際的磁碟名稱、磁碟大小和所在的區域。`DISK_SIZE` 的單位是 GB，例如如果要增加到 100GB 的話，就需要將 `DISK_SIZE` 設定為 `100GB`。

```bash
gcloud compute disks resize ${DISK_NAME} \
    --size ${DISK_SIZE} \
    --zone=${ZONE}
```

當然如果你的團隊有使用 IaC 的工具來管理 GCE 的資源的話，例如: Terraform 的話，也可以直接在 Terraform 的配置檔中修改磁碟的大小，然後執行 `terraform apply` 來增加磁碟容量。

### 讓作業系統認識新的磁碟容量🔍

當增加磁碟容量以後，接下來就需要讓作業系統認識新的磁碟容量。

首先使用 `df` 和 `lsblk` 指令列出檔案系統的大小，並找出磁碟的裝置名稱。

![df的輸出結果](img/journals/gcp/gce-increased-disk-capacity/df_outputs.png "df的輸出結果")

![lsblk的輸出結果](img/journals/gcp/gce-increased-disk-capacity/lsblk_outputs.png "lsblk的輸出結果")

上面的範例中包含以下磁碟:

- `/dev/sda`：這是系統磁碟，通常是用來安裝作業系統的磁碟(開機磁碟)。
- `/dev/sdb`：這是資料磁碟，通常是用來存放資料的磁碟(非開機磁碟)。

可以看到 `/dev/sdb` 在 VM 中掛載的目錄路徑是 `/database`，而且目前的磁碟容量是 2TB。但是因為已經調整過磁碟容量了，使用 `lsblk` 指令可以看到磁碟的大小已經變成 4TB 了。

重新讀取磁碟新的分區，擴增磁碟大小以前。需要先確認分割區類型，可以使用 `sudo parted -l` 指令來查看磁碟的分割區類型。

```shell
sudo parted -l
```

![parted的輸出結果](img/journals/gcp/gce-increased-disk-capacity/parted_outputs.png "parted的輸出結果")

上面的範例中可以看到 `/dev/sdb` 的分割區類型是 xfs 的分割區類型。所以需要使用 `sudo xfs_growfs` 指令來擴增磁碟大小。

```bash
sudo xfs_growfs /database
```

如果是 ext4 的分割區類型的話，就需要使用 `sudo resize2fs` 指令來擴增磁碟大小，例如：

```bash
sudo resize2fs /dev/sdb1
```

當執行完擴增磁碟大小的指令以後，再次使用 `df` 指令來確認磁碟的容量已經增加了。

![df的輸出結果](img/journals/gcp/gce-increased-disk-capacity/df_outputs_after_resize.png "df的輸出結果")

## 參考文獻📚

- [變更永久磁碟的大小](https://docs.cloud.google.com/compute/docs/disks/resize-persistent-disk?hl=zh-tw)
