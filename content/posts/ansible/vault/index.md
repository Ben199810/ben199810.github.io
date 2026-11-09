---
title: "Vault 保護機敏資料"
date: 2026-11-09T11:56:58+08:00
draft: false
tags: ["ansible"]
description: "使用 Ansible Vault 保護機敏資料，確保敏感資訊不以明文形式暴露。"
---

## 前言 🔖

使用 Ansible 管理基礎建設時，有時候會需要配置機敏資料。但是如果寫在 playbook 裡面，這些機敏資料就會以明文的形式存在，存在被洩漏的風險。還有一種方式，透過變數可以幫不同的環境設定不同的機敏資料，有很多的方式可以取得變數(環境變數、檔案)，相對安全。但是就算另外存下來，檔案也是明文，仍然有被洩漏的風險。

為了解決這個問題，Ansible 提供了 Vault 功能，可以用來加密機敏資料，確保即使檔案被洩漏，資料也不會以明文的形式暴露。

## Vault 的使用方式 🛡

首先我們會建立一個加密的檔案，用來存放機敏資料。可以使用以下指令：

```bash
ansible-vault create secret.yml
```

執行後，會要求輸入密碼，然後進入編輯器，編輯完成後儲存，檔案就會被加密。

如果要編輯已經加密的檔案，可以使用以下指令：

```bash
ansible-vault edit secret.yml
```

也可以先解密檔案，編輯完成後再加密。指令如下：

```bash
ansible-vault decrypt secret.yml
```

編輯完成後，可以使用以下指令重新加密：

```bash
ansible-vault encrypt secret.yml
```

加密過後的檔案內容大概會像以下這樣：

```yaml
$ANSIBLE_VAULT;1.1;AES256
6162636465666768696a6b6c6d6e6f70
7172737475767778797a303132333435
36373839303132333435363738393031
32333435363738393031323334353637
```

## 在 Playbook 中使用 Vault 🔑

我會在 Playbook 中引用剛剛建立的加密檔案，通常會將機敏資料放在變數檔案中，然後在 Playbook 中使用 `vars_files` 引入。例如：

```yaml
---
- hosts: all
  vars_files:
    - secret.yml
  tasks:
    - name: 顯示機敏資料
      debug:
        msg: "{{ my_secret_variable }}"
```

⚠️ 注意：這裡只是舉例從外部的加密檔案取得機敏資料，實際生產環境的機敏資料是不應該被列印出來的。

執行 CICD 的過程需要解密的密碼，我會設置在 Jenkins 的憑證管理或全域環境變數中，然後在執行 Ansible 時使用 `--ask-vault-pass` 或 `--vault-password-file` 來提供密碼。這樣可以確保在自動化流程中，機敏資料仍然保持加密狀態，只有在需要時才會被解密使用。

我這裡是使用 Jenkins 的全域環境變數作為範例，更好的方式可採用憑證管理來存放 Vault 密碼。

例如，在 Jenkins Pipeline 中可以這樣使用：

```groovy
pipeline {
  stages {
    stage('Run Ansible Playbook') {
      steps {
        script {
          echo "🔐 Using Vault for secrets management"
          // Write the vault password to a file
          writeFile file: "${WORKSPACE}/.vault_password", text: env.ansible_vault_password
          // Set the environment variable for the vault password file
          sh "chmod 0600 ${WORKSPACE}/.vault_password"
          env.ANSIBLE_VAULT_PASSWORD_FILE = "${WORKSPACE}/.vault_password"
          // Run the Ansible playbook with the vault password file
          ansiblePlaybook(
            playbook: "${playbookName}.yaml",
            inventory: "inventory/${env.deployEnv}/hosts.ini",
            colorized: true,
            extras: "--user=${remoteUser} --vault-password-file=${env.ANSIBLE_VAULT_PASSWORD_FILE}",
            ...
          )
        }
      }
    }
  }
}
```
