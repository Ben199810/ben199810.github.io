---
title: "Control Flow"
date: 2026-08-24T11:19:17+08:00
tags: ["Ansible"]
draft: true
description: ""
---

## 前言🔖

常用的 Ansible 控制流程的範例整理

## ansible_facts 基礎條件

當作業系統是 Debian 會執行關機，條件判斷是單一的

```yaml
- name: Show facts available on the system
  ansible.builtin.debug:
    var: ansible_facts

- name: Shut down Debian flavored systems
  ansible.builtin.command: /sbin/shutdown -t now
  when: ansible_facts['os_family'] == "Debian"
```

也可以用複數的條件組合，例如: 除了作業系統以外還需要符合特定的版本才會進行關機

```yaml
- name: Shut down CentOS 6 and Debian 7 systems
    ansible.builtin.command: /sbin/shutdown -t now
    when: (ansible_facts['distribution'] == "CentOS" and ansible_facts['distribution_major_version'] == "6") or
          (ansible_facts['distribution'] == "Debian" and ansible_facts['distribution_major_version'] == "7")
```
