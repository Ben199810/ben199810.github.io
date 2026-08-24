---
title: "CICD 自動化更新Google Cloud Storage"
date: 2026-08-24T15:52:45+08:00
draft: false
tags: ["GCP", "GCS"]
description: ""
---

## 前言

管理 GCS的圖片檔案，如果透過手動的方式去新增或刪減檔案非常沒有效率。所以使用 CICD將圖片檔案自動同步到 GCS省下繁瑣的工作流程與時間。

使用的工具:

- Google Cloud Storage(GCS)
- Jenkins
- Ansible
- Terraform
- Terragrunt

## Terraform 建立 Storage

直接使用 [Google Terraforma Module](https://github.com/terraform-google-modules/terraform-google-cloud-storage/tree/v12.3.0/modules/simple_bucket)建立一個 Storage。

可以調用自己常用的參數即可，記得要查詢哪些參數是必要的值，不然資源會建立不起來。`varibles.tf`參考官方提供的文檔定義相同的類型即可。

```hcl
module "cloud-storage" {
  source  = "terraform-google-modules/cloud-storage/google//modules/simple_bucket"
  version = "~> 12.3"

  project_id                 = var.project_id
  name                       = var.name
  location                   = var.location
  labels                     = var.labels
  force_destroy              = var.force_destroy
  iam_members                = var.iam_members
  storage_class              = var.storage_class
  lifecycle_rules            = var.lifecycle_rules
  internal_encryption_config = var.internal_encryption_config
}
```

接著可以寫 `terragrunt.hcl`建構資源了。需要注意的是 Bucket的名稱必須是要唯一值，這裡有使用 iam_members開放所有的使用者都可以看到 Storage的資源。

```hcl
terraform {
  source = "${get_path_to_repo_root()}/modules/gcs"
}

include {
  path = find_in_parent_folders("root.hcl")
}

inputs = {
  name        = "mygcsx941u3jo6"
  location    = "asia-northeast1"
  iam_members = [{ member = "allUsers", role = "roles/storage.objectViewer" }]
  labels = {
    env     = "dev"
    team    = "sre"
    service = "gcs"
  }
  lifecycle_rules = [
    {
      action = {
        type = "Delete"
      }
      condition = {
        num_newer_versions = 3
      }
    }
  ]
}
```

刪除資源的策略採用版本控制的方式，如果同步資料造成資源損毀，可以快速的從介面上還原到之前的版本。發生線上問題時，可以減少 DownTime。

![gcs-version](/img/gcp/gcs-sync/gcs-version.png "GCS版本控制")

## Jenkins Pipeline

Jenkins的設計思路很簡單，將整理好的資訊傳遞給 Ansible進行部署這次要跟新的檔案到 GCS。

1. 取得專案資訊
2. 下載 Ansible 專案
3. 執行 Ansible Playbook

```groovy
pipeline {
  agent any
  stages {
    // 取得專案資訊
    stage("GitLab Repo Info") {
      steps {
        script {
          if (env.gitlabSourceNamespace != null) {
            echo "trigger from gitlab, branch/tag = ${env.gitlabBranch}"
            gitRepoSSH = "${env.gitlabSourceRepoSshUrl}"
            gitRepoName = gitRepoSSH.split('/')[-1].replace('.git', '')
            tag = env.gitlabBranch.split('/')[-1]
          }
          echo "gitRepoSSH = ${gitRepoSSH}"
          echo "gitRepoName = ${gitRepoName}"
          echo "tag = ${tag}"
          env.GIT_REPO_SSH = gitRepoSSH
          env.GIT_REPO_NAME = gitRepoName
          env.TARGET_TAG = tag
        }
      }
    }
    // Clone Ansible
    stage('Clone Ansible') {
      steps {
        cleanWs()
        dir("${WORKSPACE}/ansible") {
          checkout scm: [
          $class: 'GitSCM',
          userRemoteConfigs: [[url: "git@${env.gitlab_domain}/ansible.git"]],
          branches: [[name: "master"]],
          extensions: [[$class: 'CloneOption', timeout: 300]]
          ]
        }
      }
    }
    // 執行 Ansible Playbook
    stage('Deploy to Dev GCS via Ansible') {
      when {
        environment name: 'TARGET_TAG', value: 'dev'
      }
      steps {
        withCredentials([
          file(credentialsId: 'On-premises-gcs-bucket-key', variable: 'GCP_KEY_PATH'),
          string(credentialsId: 'On-premises-gcs-bucket', variable: 'GCS_BUCKET_NAME')
        ]) {
          script {
            def extraVars = [
              git_repo_ssh: env.GIT_REPO_SSH,
              git_repo_name: env.GIT_REPO_NAME,
              branch_name: env.TARGET_TAG,
              gcp_key_path: env.GCP_KEY_PATH,
              gcs_bucket_name: env.GCS_BUCKET_NAME,
              env: env.TARGET_TAG
            ]
            dir("${WORKSPACE}/ansible") {
              ansiColor('xterm') {
                ansiblePlaybook(
                  playbook: 'upload_imgs_bucket_deploy.yaml',
                  inventory: "inventory/${env.TARGET_TAG}/hosts.ini",
                  extraVars: extraVars,
                  colorized: true
                )
              }
            }
          }
        }
      }
    }
  }
  post {
    always {
      cleanWs()
    }
  }
}
```

⭐️ 補充說明:

用來獲得 GCS存取權限的 Key需要到 ServiceAccount建立，建立完以後放在 Jenkins的 Credentials。

## Ansible Playbook

1. 將圖片專案下載
2. 驗證並登入 GCP
3. 開始同步圖片檔案

```yaml
---
- name: get assets repository url
  delegate_to: localhost
  run_once: true
  set_fact:
    git_repo_url: "{{ 'ssh://git@' + gitlab_domain + '/assets.git' }}"
  tags: pull

- name: clone assets repository
  delegate_to: localhost
  run_once: true
  git:
    repo: "{{ git_repo_url }}"
    dest: "{{ role_path }}/files/"
    version: "{{ branch_name | default('dev') }}"
    depth: 1
  tags: pull

- name: 驗證並登入 GCP Service Account
  ansible.builtin.command: >
    gcloud auth activate-service-account --key-file={{ gcp_key_path }}
  changed_when: false

- name: 將圖片同步上傳至 GCP Bucket 的 assets/ 資料夾
  ansible.builtin.command: >
    gsutil -m rsync -r -d -x "^(\\.git.*)$" {{ role_path }}/files/assets/ gs://{{ gcs_bucket_name }}/assets
  register: rsync_result
  changed_when: "'Copying' in rsync_result.stderr or 'Removing' in rsync_result.stderr"

- name: 顯示同步輸出訊息
  ansible.builtin.debug:
    var: rsync_result.stderr_lines
```

成功執行以後就可以到 Bucket上查看檔案有沒有更新，通常我會直接查看`上次修改時間`。

![](/img/gcp/gcs-sync/last-edit-time.png)
