---
title: "Ansible 自動化管理的實務經驗"
date: 2026-10-14T09:10:55+08:00
draft: true
description: ""
---

## 前言 🔖

許多的企業實作軟體自動化流程時，都會使用到 ansible 管理大量的服務器或是微服務。但是隨著業務的發展，一開始簡單的結構 playbook 可能已經沒有辦法滿足團隊管理的需求。因此如何管理好 ansible 也是一個實務上我們必須要去關注的一個問題。

## Inventory 📌

在實務經驗上，inventory 通常不會只有ㄧ個檔案，在環境保持一致性以及管理方便的前提下，會將不同環境的 inventory 分開管理，我通常會在將不同的環境進行分組，例如:

```shell
my-ansible
└──inventory
   ├──dev
   │  ├──hosts.ini
   │  └──group_vars
   │      └──all.yml
   ├──qa
   │  ├──hosts.ini
   │  └──group_vars
   │      └──all.yml
   └──prod
      ├──hosts.ini
      └──group_vars
          └──all.yml
```

當我需要對特定的環境進行操作時，我只需要指定對應的 inventory 底下的環境目錄即可，例如:

```shell
ansible-playbook -i inventory/dev/hosts.ini playbook.yml
```

hosts.ini 會定義 Hosts 的群組，我認為比較好的做法是將性質的 Hosts 需要在同一組中，例如: 有三台 API 的服務器可以放在同一組中，像這樣:

```ini
[api_servers]
10.93.11.1
10.93.11.2
10.93.11.3
```

不推薦使用服務名稱作為群組，雖然有 children group 可以覆蓋這個問題。但隨著服務數量的增加，hosts.ini 變得很冗餘且複雜，維護起來也會更加困難。例如:

```ini
[api_services]
10.93.11.1
10.93.11.2
10.93.11.3
[membercenter:children]
api_services
[replay:children]
api_services
[payment:children]
api_services
```

這三個 API 服務的 playbook 實際上都是對 api_servers 這個群組進行操作的，這樣其實沒有必要再額外建立多個服務名稱的子群組。

## Roles 📌

一開始簡單的 playbook 中，會寫滿各種的 tasks，伴隨著管理越來越多的 playbook，應該會開始思考有哪些重複的操作可以抽象出來，這時候我們可以開始規劃 roles。roles 可以想像成一個角色必須要完成的任務，playbook 可以引用單一或者多個 roles。

舉一個例子就是一個演員拿到了 playbook(劇本)，劇本上面有一個或者多個角色，有的時候同一個演員可能會飾演多個角色。很合理吧🤣，演員就會照個劇本上的角色去完成相應的角色任務。

在 roles 目錄下，我習慣會將每個角色單獨建立一個目錄，可以清楚地知道這個角色的職責範圍到哪裡，例如:

```shell
my-ansible
└──roles
   ├──api_service_deploy # API 服務部署角色
   │  ├──tasks
   │  │   └──main.yml
   │  ├──handlers
   │  │   └──main.yml
   │  ├──templates
   │  ├──files
   │  └──defaults
   │      └──main.yml
   └──game_server_deploy # 遊戲服務部署角色
      ├──tasks
      │   └──main.yml
      ├──handlers
      │   └──main.yml
      ├──templates
      ├──files
      └──defaults
          └──main.yml
```

使用這種方式管理 roles，可以讓每個角色的職責範圍更加清晰，如果 roles 之間有共用的邏輯也可以抽象成獨立的角色，供其他角色引用。

接著我們近一步來看看 roles 的目錄結構，以前我會將所有的檔案都放在 templates 的目錄底下，使用 `ansible.builtin.template` 模組去部署，但我覺得更好的方式區分 jinja2 的範本檔案與其他靜態的檔案，所以我會將靜態的檔案放在 files 目錄底下，這樣在使用 `ansible.builtin.copy` 模組去部署靜態檔案時會更加清晰明瞭。