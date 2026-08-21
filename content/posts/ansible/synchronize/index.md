---
title: "Synchroize 同步遠端伺服器檔案"
date: 2026-08-21T10:11:09+08:00
draft: true
tags: ["Ansible"]
description: ""
---

## 前言🔖

部署時，需要將版本控制文件同步到伺服器上，最常使用到 Synchroize 模組來幫助我。

例如: 同步 Nginx 伺服器上的 Config 設定路由規則等...

## 範例📌

通常會更新 Nginx 的目標檔案與目錄總共有兩個 `/etc/nginx/nginx.conf`、`/etc/nginx/conf.d`。

src 代表來源檔案的路徑，dest 代表目標檔案的路徑，還可以使用 rsync_opts 配置檔案的使用者、群組以及權限。

⭐️ 補充: 同步 conf.d 目錄時，src 的路徑需要在最後加上 `/`，如果沒有加上 / 會變成在伺服器上看到 `/etc/nginx/conf.d/conf.d` 目標的目錄底下又新增了一個目錄，/ 的作用是告訴 synchronize 模組，同步 conf.d 目錄底下的所有檔案，而不是目錄本身。

```yaml
- name: Sync Nginx configuration
  become: true
  ansible.posix.synchronize:
    src: "{{ role_path }}/templates/nginx.conf"
    dest: /etc/nginx/nginx.conf
    rsync_opts:
      - "--chown=root:root"
      - "--chmod=0644"

- name: Sync Nginx conf.d
  become: true
  ansible.posix.synchronize:
    src: "{{ role_path }}/templates/conf.d/"
    dest: /etc/nginx/conf.d
    rsync_opts:
      - "--chown=root:root"
      - "--chmod=D755,F644"
    delete: true
```

同步完設定檔案以後，就可以接著 Reload Nginx 了!

先使用 `nginx -t` 檢查設定檔有沒有異常，沒有異常才可以執行 Reload。

```yaml
- name: test nginx configuration
  become: true
  ansible.builtin.shell: nginx -t
  register: nginx_test

- name: Reload Nginx
  become: true
  ansible.builtin.systemd:
    name: nginx
    state: reloaded
  when: nginx_test.rc == 0
```
