---
title: "Ansible - 輕鬆管理自動化部署"
date: 2026-07-29T16:49:16+08:00
draft: false
tags: ["Ansible"]
description: "Ansible 是一個幫助自動化 IT 的基礎建設工具。它可以配置系統、部署軟體以及協調更複雜的 IT 任務，可以大幅度的減少重複性工作，提高效率。"
---

## 簡介🔖

Ansible 是一個幫助自動化 IT 的基礎建設工具。它可以配置系統、部署軟體以及協調更複雜的 IT 任務，可以大幅度的減少重複性工作，提高效率。更棒的是，Ansible 是一個無代理的工具，這意味著它不需要在目標機器上安裝任何軟體，只需要透過 SSH 連線即可進行操作。

Ansible 使用 YAML 語言來描述自動化任務，非常容易閱讀和理解。Ansible 的基礎是任務(Tasks)，可以理解為一個操作步驟或者是一個命令。多個任務可以組成一個劇本(Playbook)，這個劇本可以定義一個完整的自動化流程，從安裝軟體到配置系統，甚至是部署應用程式。

本文章會使用 Docker 在本地端建立一個 Ansible 的測試環境，對兩個 Ubuntu 虛擬機器進行操作。

Github Repository: [ansible_practice](https://github.com/Ben199810/ansible_practice)

## 環境建置📌

- macOS 26.1
- Docker Engine 29.0.2
- Docker Desktop 4.52.0 (210994)
- Docker Compose version v2.40.3-desktop.1
- ubuntu:22.04

### 管理節點🖥️

先使用 Dockerfile 建立 Ubuntu 22.04 的管理節點(Managed Node)，管理節點的意思就是受管理的節點，控制節點(Controller Node)會透過 SSH 連線到管理節點，並執行 Ansible 的任務。

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
  openssh-server \
  python3 \
  sudo

RUN mkdir /var/run/sshd
RUN echo 'root:rootpassword' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
```

⚠️ 注意: 本文章在 Dockerfile 中，更改了 SSH 的設定，允許 root 使用密碼登入，這在實務上是不建議的，請不要在生產環境中使用。

使用 docker-compose.yml 建立兩個 Ubuntu 22.04 的管理節點，並且將它們的 SSH port 映射到本地端的 2221 與 2222。

```yaml
services:
  web1:
    build:
      context: .
      dockerfile: managed.dockerfile
    container_name: web1
    tty: true
    ports:
      - "2221:22"
    networks:
      - ansible_network
  web2:
    build:
      context: .
      dockerfile: managed.dockerfile
    container_name: web2
    tty: true
    ports:
      - "2222:22"
    networks:
      - ansible_network
networks:
  ansible_network:
    driver: bridge
```

執行 `docker compose up -d` 可以看到兩個 Ubuntu 22.04 的管理節點已經啟動。

![managed_nodes_up](/img/posts/ansible/managed_nodes_up.png "managed_nodes_up")

### 控制節點🖥️

使用 Dockerfile 建立 Ubuntu 22.04 的控制節點(Controller Node)，控制節點的意思就是負責管理其他節點的節點。

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
  ansible \
  openssh-client \
  sshpass
```

建立 inventory 跟 playbook 的資料夾，這兩個資料夾會放置 Ansible 的設定檔案與自動化任務。

```bash
mkdir -p inventory playbooks
```

inventory 資料夾中建立 `hosts.ini`，這個檔案會定義管理節點的資訊。在 `hosts.ini` 中，可以定義群組(Host Group)與變數(Variables)，群組可以將多個管理節點分組，變數可以定義一些群組的共用的設定。

```ini
[web]
ubuntu1 ansible_host=ubuntu1 ansible_user=root ansible_password=root123 ansible_port=22
ubuntu2 ansible_host=ubuntu2 ansible_user=root ansible_password=root123 ansible_port=22

[web:vars]
ansible_connection=ssh
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
```

playbooks 資料夾中建立一個安裝 Nginx 的 playbook `install_nginx.yaml`，這個劇本會在管理節點上安裝 Nginx。

```yaml
- name: Install and start Nginx on Ubuntu containers
  hosts: web
  become: true
  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes

    - name: Install nginx
      apt:
        name: nginx
        state: present

    - name: Ensure nginx is started
      service:
        name: nginx
        state: started
        enabled: yes
```

inventory 與 playbook 都準備好了之後，可以更新 docker-compose.yml，將控制節點加入到同一個網路中，並且將 inventory 與 playbook 的資料夾掛載到容器中。

```yaml
services:
  controller:
    build:
      context: .
      dockerfile: ansible.dockerfile
    container_name: controller
    tty: true
    stdin_open: true
    volumes:
      - ./inventory:/work/inventory
      - ./playbooks:/work/playbooks
    networks:
      - ansible_network
    depends_on:
      - web1
      - web2
```

重新啟動 Docker Compose，可以看到控制節點已經啟動。

![controller_node_up](/img/posts/ansible/controller_node_up.png "controller_node_up")

## 執行 Ansible Playbook🚀

上述的環境建置完成後，本機電腦環境中已經有三個 Docker 容器，分別是兩個管理節點與一個控制節點。接下來可以透過控制節點執行 Ansible Playbook，對管理節點進行操作。

進入控制節點的容器，並且切換到 work 資料夾，這個資料夾中有 inventory 與 playbooks 的資料夾。

```bash
docker exec -it controller bash
cd /work
```

在執行 palybook 之前，可以先測試是否可以透過 SSH 連線到管理節點，使用 `ansible` 指令來測試。

`web` 代表定義的群組，`-m ping` 代表使用 ping 模組來測試連線。

```bash
ansible -i inventory/hosts.ini web -m ping
```

如果看到兩台 web 伺服器都回應 pong，代表控制節點可以成功連線到管理節點。

![ansible_ping](/img/posts/ansible/ansible_ping.png "ansible_ping")

接著可以執行安裝 Nginx 的 playbook，使用 `ansible-playbook` 指令來執行。

```bash
ansible-playbook -i inventory/hosts.ini playbooks/install_nginx.yaml
```

![ansible_playbook](/img/posts/ansible/ansible_playbook.png "ansible_playbook")

完成以後，可以檢查管理節點是否有安裝 Nginx。

```bash
docker exec -it web1 nginx -v
docker exec -it web2 nginx -v
```

或者可以檢查 Nginx 是否有啟動。

```bash
docker exec -it web1 service nginx status
docker exec -it web2 service nginx status
```

## 結論📝

透過上述的練習，可以知道有多台管理節點的情況下，Ansible 可以同時對多台管理節點進行操作，這樣可以大幅度的減少重複性工作，提高效率。尤其是在務實上需要對大量的伺服器進行操作時，Ansible 可以幫助我們節省大量的時間與人力成本。
