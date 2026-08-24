---
title: "GCE 永久磁碟掛載實作過程紀錄"
date: 2026-01-20T16:25:52+08:00
draft: false
tags: ["GCP", "GCE", "Disk"]
description: ""
---

## 前言🔖

近期在公司內部有需要建置 VM 提供給 DBA 的同仁，有提出需要掛載額外的磁碟空間，經過一番研究後，決定使用 GCP 的 GCE 永久磁碟 (Persistent Disk) 來達成這個需求。會使用附加磁碟的方式，主要是因為這樣可以讓 VM 的系統磁碟與資料磁碟分開管理，方便日後的維護與擴充。

## 建置步驟🛠

一開始會透過 IaC 工具先建立好 VM 與附加磁碟的資源，以下是使用 Terraform 的範例程式碼：

```hcl
resource "google_compute_instance" "default" {
  name         = "example-instance"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-9"
    }
  }

  attached_disk {
    source = google_compute_disk.attached_disk.id
    mode   = "READ_WRITE"
  }

  network_interface {
    network = "default"
    access_config {}
  }
}
```

建立完 VM 與附加磁碟後，接下來需要在 VM 內部進行磁碟的初始化與掛載。以下是步驟說明：

## 磁碟初始化與掛載🔧

- 將磁碟連接至 VM
  如何確認已經連接成功，可以透過 GCP 控制台或是使用 `lsblk` 指令查看磁碟列表。
  控制台的畫面如下圖所示：
  ![GCP 控制台磁碟連接畫面](/img/gcp/gce-disk-mount/additional-disk.png)

- 在 VM 內部初始化磁碟
  已經連接成功後，接下來需要在 VM 內部進行磁碟的初始化。可以先需照序號列出磁碟資訊，確認新磁碟的裝置名稱。

  ```bash
  ls -l /dev/disk/by-id/
  ```

  從輸出中找到磁碟序號，如下圖所示：
  ![磁碟序號範例](/img/gcp/gce-disk-mount/get-disk-id.png)

- 初始化磁碟
  使用 `mkfs.xfs` 指令來初始化磁碟，以下是範例指令：

  ```bash
  sudo mkfs.xfs /dev/sdb
  ```

  這裡需要注意的是初始化磁碟，因為這裡要使用的檔案系統是 XFS，所以使用 `mkfs.xfs` 指令。

- 建立掛載點並掛載磁碟
  接下來需要建立掛載點，並將磁碟掛載到該目錄下：

  ```bash
  mkdir -p /mnt/data
  mount /dev/sdb /mnt/data
  ```

- 設定開機自動掛載
  為了讓磁碟在 VM 重啟後能夠自動掛載，需要編輯 `/etc/fstab` 檔案，加入以下內容：

  ```bash
  echo "UUID=$UUID /mnt/data xfs defaults,discard 0 0" >> /etc/fstab
  ```

  UUID 可以透過 `blkid` 指令來取得：

  ```bash
  UUID=$(blkid -s UUID -o value /dev/sdb)
  ```

## 結語📝

透過以上的步驟，我們成功地在 GCE VM 上掛載了額外的永久磁碟，並且設定了開機自動掛載。這樣的架構不僅提升了資料的管理彈性，也方便日後的擴充與維護。如果有需要更多磁碟空間，只需再新增附加磁碟並重複上述步驟即可。

## 參考文獻📚

- [Terraform GCE Instance Documentation](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_instance)
- [將永久磁碟新增至 VM](https://cloud.google.com/distributed-cloud/hosted/docs/latest/appliance/application/ao-user/vms/manage-storage/add-a-vm-disk?hl=zh-tw)
