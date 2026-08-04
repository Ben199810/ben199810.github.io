---
title: "Jinja2 Dryrun"
date: 2026-07-21T16:23:02+08:00
draft: false
description: "調整 templates jinja2 模板，使用 dryrun 方式，先在本地端渲染模板，確認語法有無錯誤。"
tags: ["ansible", "jinja2", "dryrun"]
---

## 簡介

調整 templates jinja2 模板，使用 dryrun 方式，先在本地端渲染模板，確認語法有無錯誤。

專案結構，參考樹狀圖。

```text
.
├── README.md
├── ansible.cfg
├── nginx_deploy.yaml
├── inventory
│   ├── dev
│   │   ├── group_vars
│   │   │   └── all.yaml
│   │   └── hosts.ini
│   ├── prd
│   │   ├── group_vars
│   │   │   └── all.yaml
│   │   └── hosts.ini
│   └── qa
│       ├── group_vars
│       │   └── all.yaml
│       └── hosts.ini
├── roles
    └── nginx_deploy
        ├── tasks
        │   └── main.yaml
        └── templates
            ├── conf.d
            │   └── api.conf.j2
            └── docker-compose.yaml.j2
```

執行 dryrun 渲染模板，使用 `--check` 跟 `--diff` 參數，確認模板渲染結果。

```bash
ansible-playbook -i inventory/prd/hosts.ini nginx_deploy.yaml --connection=local --check --diff -e "ansible_user=${USER}"
```

## 遇到的問題

dry-run 渲染模板時，ansible.cfg 設定 stdout_callback = skippy，導致出現錯誤訊息。

```text
[ERROR]: Could not load 'skippy' callback plugin.
```

## 解決方式

將 ansible.cfg 設定 stdout_callback = default，或者執行時使用環境變數來覆蓋這個設定。例如：

```bash
ANSIBLE_STDOUT_CALLBACK=default ansible-playbook nginx_deploy.yaml -i inventory/dev
```
