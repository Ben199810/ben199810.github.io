---
title: "Terraform Flatten 函數的使用範例"
date: 2026-08-18T09:38:46+08:00
draft: false
tags: ["Terraform"]
description: "自己看官方文件後，依據自己的理解重新再打一次使用方式，增加了比較詳細的說明，方便日後查詢能更好的重新理解"
---

## 基本用法

flatten 接受一個 list，會將 list 中所有的 list 元素替換成 list 的內容。

```txt
> flatten([["a", "b"], [], ["c"]])
["a", "b", "c"]
```

## 使用情境

在 terraform中，常常會定義巢狀的 variable，例如:

```hcl
variable "networks" {
  type = map(object({
    cidr_block = string
    subnets = map(object({ cidr_block = string }))
  }))
  default = {
    "private" = {
      cidr_block = "10.1.0.0/16"
      subnets = {
        "db1" = {
          cidr_block = "10.1.0.0/24"
        }
        "db2" = {
          cidr_block = "10.1.1.0/24"
        }
      }
    },
    "public" = {
      cidr_block = "10.2.0.0/16"
      subnets = {
        "webserver" = {
          cidr_block = "10.2.1.0/24"
        }
        "email_server" = {
          cidr_block = "10.2.2.0/24"
        }
      }
    }
    "dmz" = {
      cidr_block = "10.3.0.0/16"
      subnets = {
        "firewall" = {
          cidr_block = "10.3.1.0/24"
        }
      }
    }
  }
}
```

可以看到網路的變數使用了巢狀的結構定義了 networks與 subnets，頂層的 network 涵蓋了 subnet 的資訊，這樣的樹狀結構是很常有的。

如果是對網路的 resource區塊，我們可以直接使用這個變數:

```hcl
resource "aws_vpc" "example" {
  for_each = var.networks

  cidr_block = each.value.cidr_block
}
```

對於子網路的 resource區塊，我們需要將結構做扁平化處理。

```hcl
locals {
  # flatten 確保此局部值是一個扁平的 list[object{}]，而不是 list[list[object{}]]
  network_subnets = flatten([
    for network_key, network in var.networks : [
      for subnet_key, subnet in network.subnets : {
        network_key = network_key
        subnet_key  = subnet_key
        network_id  = aws_vpc.example[network_key].id
        cidr_block  = subnet.cidr_block
      }
    ]
  ])
}
```

locals.network_subnets 實際展開的結果:

```hcl
network_subnets = [
  {
    network_key = "private"
    subnet_key  = "db1"
    network_id  = aws_vpc.example["private"].id
    cidr_block  = "10.1.0.0/24"
  },
  {
    network_key = "private"
    subnet_key  = "db2"
    network_id  = aws_vpc.example["private"].id
    cidr_block  = "10.1.1.0/24"
  },
  {
    network_key = "public"
    subnet_key  = "webserver"
    network_id  = aws_vpc.example["public"].id
    cidr_block  = "10.2.1.0/24"
  },
  {
    network_key = "public"
    subnet_key  = "email_server"
    network_id  = aws_vpc.example["public"].id
    cidr_block  = "10.2.2.0/24"
  },
  {
    network_key = "dmz"
    subnet_key  = "firewall"
    network_id  = aws_vpc.example["dmz"].id
    cidr_block  = "10.3.1.0/24"
  }
]
```

接著將 locals.network_subnets帶入到 subnets的 resource做使用:

```hcl
resource "aws_subnet" "example" {
  # local.network_subnets 是一個 list，先將它轉換成 map，這裡使用 network_key與 subnet_key組成唯一的 key值
  for_each = tomap({
    for subnet in local.network_subnets : "${subnet.network_key}.${subnet.subnet_key}" => subnet
  })

  vpc_id            = each.value.network_id
  availability_zone = each.value.subnet_key
  cidr_block        = each.value.cidr_block
}
```

## 參考文件

- [flatten Function](https://developer.hashicorp.com/terraform/language/functions/flatten)
