---
title: "Jinja2 Control Flow"
date: 2026-08-24T11:36:15+08:00
draft: true
description: ""
---

## 前言🔖

Ansible常會使用 jinja2模板進行動態的檔案建立以及配置，整理常用的控制流程語法。一開始撰寫模板配置的時候，很常會因為空格、換行符等..造成模板渲染出來後跑版、嚴重一點會造成設定配置無效。所以我習慣會在 jinja2模板開頭新增 `#jinja2: trim_blocks: True, lstrip_blocks: True`

- trim_blocks 移除 jinja2語句塊({% if %}、{% for %})後面的第一個換行符，防止渲染後留下多餘的空行
- lstrip_blocks 移除行首到 jinja2 語句塊之間所有空格和制表符(Tab)，允許你在模板中為了排版好看縮進 `{% ... %}`最後渲染的文件中不會戴上這些縮進的空白

## If📌

```jinja2
{% if kenny.sick %}
    Kenny is sick.
{% elif kenny.dead %}
    You killed Kenny!  You bastard!!!
{% else %}
    Kenny looks okay --- so far
{% endif %}
```
