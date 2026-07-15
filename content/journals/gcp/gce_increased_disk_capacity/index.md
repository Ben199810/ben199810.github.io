---
title: "GCE 擴充永久磁碟大小"
date: 2026-03-31T09:10:39+08:00
draft: false
tags: ["GCP", "GCE", "Disk", "VM", "Google Cloud"]
description: "分享在 GCE 上增加永久磁碟容量的實作步驟，包含增加磁碟容量以及讓作業系統認識新的磁碟容量的過程。本文將介紹如何使用 gcloud CLI 或 Terraform 來增加磁碟容量，以及如何使用 df、lsblk 和 parted 等指令來確認磁碟的狀態，最後使用 xfs_growfs 或 resize2fs 指令來擴增磁碟大小。"
---

## 前言🔖

最近需要幫助公司的 Elasticsearch 增加磁碟容量，過程中參考了 Google Cloud 的官方文件。

發現增加磁碟容量的過程其實非常簡單，主要分為兩個步驟：第一步是增加實體磁碟容量，第二步是讓作業系統認識新的磁碟容量。

知道了這兩個步驟以後，整個過程就非常簡單了。

‼️注意: 這次的文章是紀錄增加永久磁碟容量的過程，如果要增加開機磁碟容量的話，可以透過參考文獻的連結來了解更多細節。

## 實作步驟📌

### 增加磁碟容量🔍

首先，要增加實體磁碟容量。

可以使用 Google Cloud Console 的 UI 介面來增加磁碟容量，或者使用 gcloud CLI 的方式來增加磁碟容量。

注意: 這裡的 `DISK_NAME` 、`DISK_SIZE` 和 `ZONE` 都需要替換成實際的磁碟名稱、磁碟大小和所在的區域。`DISK_SIZE` 的單位是 GB。

例如: 磁碟大小要設定 100GB 的話，就需要將 `DISK_SIZE` 設定為 `100GB`。

```bash
gcloud compute disks resize ${DISK_NAME} \
    --size ${DISK_SIZE} \
    --zone=${ZONE}
```

當然，如果團隊有使用 IaC 工具來管理 GCP 資源。

例如: Terraform，也可以直接在 Terraform 的配置檔中修改磁碟的大小，然後執行 `terraform apply` 來增加磁碟容量。

### 讓作業系統認識新的磁碟容量🔍

增加實體磁碟容量以後，接下來需要讓作業系統重新認識磁碟容量。

首先，使用 `df` 和 `lsblk` 指令列出檔案系統的大小，並找出磁碟的裝置名稱。

下圖的範例中包含以下磁碟:

- `/dev/sda`：這是系統磁碟，通常是用來安裝作業系統的磁碟(開機磁碟)
- `/dev/sdb`：這是資料磁碟，通常是用來存放資料的磁碟(非開機磁碟)

可以看到 `/dev/sdb` 在 VM 中掛載的目錄路徑是 `/database`，目前系統內顯示的磁碟容量是 2TB。

![df的輸出結果](img/journals/gcp/gce_increased_disk_capacity/df_outputs.png "df的輸出結果")

如果使用 `lsblk` 指令來查看磁碟大小，會發現 `/dev/sdb` 的大小是 4TB‼️

因為先前已經在 GCP 上將實體磁碟容量增加到 4TB，但是作業系統還沒有認識到新的磁碟容量，所以目前系統內顯示的磁碟容量跟實際的磁碟容量不一致。

![lsblk的輸出結果](img/journals/gcp/gce_increased_disk_capacity/lsblk_outputs.png "lsblk的輸出結果")

讓系統重新讀取磁碟的分區之前，需要先確認磁碟分割區類型，可以使用 `sudo parted -l` 指令來查看磁碟的分割區類型。

```shell
sudo parted -l
```

下圖的範例中可以看到 `/dev/sdb` 的 `File system` 是 `xfs`，所以需要使用 `sudo xfs_growfs` 指令重新讀取磁碟的分區。

![parted的輸出結果](img/journals/gcp/gce_increased_disk_capacity/parted_outputs.png "parted的輸出結果")

```bash
sudo xfs_growfs ${MOUNT_DIR}
```

如果 `File system` 是 `ext4` 的話，就需要使用 `sudo resize2fs` 指令來重新讀取磁碟的分區。

```bash
sudo resize2fs /dev/${DEVICE_NAME}
```

重新讀取磁碟的分區以後，再使用 `df` 指令來確認磁碟的容量是否已經增加。

下圖的範例中可以看到 `/dev/sdb` 的磁碟容量已經從 2TB 增加到 4TB，這樣就完成了整個增加磁碟容量的過程。

![df的輸出結果](img/journals/gcp/gce_increased_disk_capacity/df_outputs_after_resize.png "df的輸出結果")

## 參考文獻📚

- [變更永久磁碟的大小](https://docs.cloud.google.com/compute/docs/disks/resize-persistent-disk?hl=zh-tw)
