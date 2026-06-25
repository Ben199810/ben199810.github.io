---
title: "使用 docker swarm 管理 container"
date: 2026-06-24T15:14:57+08:00
draft: false
description: ""
---

## 前言🔖

最近已經在公司內部陸陸續續的將 api 服務，都轉成了 docker。有時候遇到尖峰時間，有些 api 服務只有兩個可能就會不夠應對線上的大流量，導致需要馬上開新的 vm，接著部署 api 服務再將新的 vm 新增到負載平衡的後端群組裡。這個過程非常的麻煩。有時候 api server 只是幾個特定的 api 快要撐不住了。就需要再花費一台新的 vm 費用，怎麼想都很不划算。所以需要用 docker swarm 幫助我們擴縮 api container，在尖峰時間，特定的 api 能快速擴展更多的 container。過了離峰時間時間時，api container 可以快速縮減。這樣的話就可以省去了繁瑣的 sop，以及兼顧成本。

## docker swarm 簡介📝

docker swarm 是透過 manager node 管理 worker node 的方式，來達到快速擴縮 container 的功能。manager 就像是大腦可以調度 container 到指定的 worker node 上運行。

## 實作🛠

首先要先建立一個 docker swarm 的叢集：

```bash
docker swarm init

# 如果 vm 上有多個 IP 地址，需要使用 --advertise 參數指定要使用的 IP 地址
docker swarm init --advertise-addr <IP_ADDRESS>
```

初始化建立完成以後，會產生一個 token，這個 token 是用來讓 worker node 加入 swarm 的。

```bash
# 在 worker node 上使用 token 加入 swarm
docker swarm join --token <TOKEN> <MANAGER_IP>:2377
```

如果沒有忘記 token 的話，可以使用以下指令來查看 token：

```bash
# 查看 worker node 的 token
docker swarm join-token worker
```

如果是要讓 manager node 加入 swarm 的話可以用：

```bash
# 查看 manager node 的 token
docker swarm join-token manager
```

完成叢集的建置以後，可以用以下指令來查看 node 的狀態：

```bash
docker node ls
```

接著在 manager node 上，開始部署 docker stack。因為我們原來是用 docker compose 來管理 container，所以轉換到 docker swarm 會有幾個需要注意的地方。

可以參考下面的 yaml 範例，已經轉換成 docker swarm 支援的格式了。

```yaml
services:
  api:
    image: my-api:latest
    ports:
      - "3000:3000"
    configs:
      - source: api_config
        target: /app/config.json
    env_file:
      - .env
    volumes:
      - logs:/app/logs
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: "0.5"
          memory: "512M"
        reservations:
          cpus: "0.25"
          memory: "256M"
      restart_policy:
        condition: any
      placement:
        constraints:
          - "node.role == worker"
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

原本的 api config 我們是透過 volume 掛載到 container 裡面，但是如果換成 docker swarm 的話，每一台 worker node 都會需要建立一個 config 文件，這樣才能讓每一個 container 都能夠讀取到 config 文件。為了要解決這個問題，我們會透過 docker swarm 的 config 功能，將 config 文件上傳到 swarm 叢集裡面，這樣每一個 container 都能夠讀取到 config 文件。

創建 docker swarm config：

```bash
docker config create api_config config.json
```

創建以後，可以用 ls 指令查看 config 有沒有成功創建：

```bash
docker config ls
```

## 過程中遇到的問題❓

有遇到當我在 manager node 上已經登入過 docker registry 了，實際執行部署指令的時候，container 沒辦法成功在 worker node 上面運行。

可以先透過指令查詢 stack 的 task 狀態：

```bash
docker stack ps <STACK_NAME> --no-trunc
```

--no-trunc 是為了要顯示完整的錯誤訊息，不被省略。這個層級的 log 資訊可以理解為 kubernetes deployment 的 event log。

透過 stack 提供的 log 訊息，我發現 worker node 沒有辦法 pull image，因為 worker node 沒有登入 docker registry，那有什麼方式可以解決？

我們可以在執行部署的時候，透過 --with-registry-auth 參數，這個參數可以將 manager node 登入 docker registry 的認證資訊，傳遞給 worker node，因為通常我們只會在 manager node 執行部署，所以這個方式我認為是最好的解決方案。

```bash
docker stack deploy --with-registry-auth -c docker-compose.yml <STACK_NAME>
```

完成以後，可以透過以下指令查看 stack 的 service 狀態：

```bash
docker stack services <STACK_NAME>
```

如果發現 container 一直 crash 重啟，就需要繼續往 container 裡面查看 log，找出 container crash 的原因。

```bash
docker service logs <SERVICE_NAME>
```

如果服務都順利啟動了以後，就可以在 manager node 上面 curl 測試看看 api container 是否有正常運作。

```bash
curl http://<MANAGER_IP>:3000/api/health
```

## 擴縮 container📦

這樣我們就完成了 docker swarm 的部署，接下來就可以嘗試使用 docker swarm 對 container 進行擴縮。

可以透過以下指令：

```bash
docker service scale <SERVICE_NAME>=<NUMBER_OF_REPLICAS>
```

## 結論🎯

透過這次的實作跟了解 docker swarm 的運作方式，我們可以在尖峰時間快速的擴縮 container，這樣就可以省去繁瑣的 sop，減少了時間跟成本。
