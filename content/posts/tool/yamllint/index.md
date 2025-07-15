---
title: "Yamllint"
date: 2025-07-14T08:56:36+08:00
draft: true
description: ""
---
## 介紹

yamllint 不僅檢查語法的有效性，還檢查諸如鍵重複之類的異常情況以及諸如行長度、尾隨空格、縮排等外觀問題。有時候尾隨空格可能會導致 YAML 文件解析錯誤，這在處理大型配置文件時尤其重要。

對於時常維護大量 YAML 文件的開發者來說是一個非常有用的工具。

## 安裝

```bash
brew install yamllint
```

## 使用

當前的目錄下對所有 YAML 文件進行檢查。

如果有 `.yamllint` 配置文件，預設會自動載入文件的配置。

```bash
yamllint .
```

## 預設

yamllint 有一些預設檔案配置。

```yaml
---

yaml-files: # 這個配置指定了要檢查的 YAML 文件類型。
  - '*.yaml'
  - '*.yml'
  - '.yamllint'

rules:
  anchors: enable
  braces: enable
  brackets: enable
  colons: enable
  commas: enable
  comments:
    level: warning
  comments-indentation:
    level: warning
  document-end: disable
  document-start:
    level: warning
  empty-lines: enable
  empty-values: disable
  float-values: disable
  hyphens: enable
  indentation: enable
  key-duplicates: enable
  key-ordering: disable
  line-length: enable
  new-line-at-end-of-file: enable
  new-lines: enable
  octal-values: disable
  quoted-strings: disable
  trailing-spaces: enable
  truthy:
    level: warning
```

yamllint 還有另一個預定義的配置叫 `relaxed`，顧名思義就是放寬檢查，寬容性更高。

```shell
yamllint -d relaxed file.yml
```

## 配置

如果需要自定義配置，可以不必全部的配置都重新定義一次。使用 `extends` 關鍵字擴展預設配置。

```yaml
extends: default
line-length:
  max: 80
  level: warning
```

## 忽略檢查

如果像 helm template 雖然是 YAML 文件，但是使用 go template 語法，這時候可以使用 `ignore` 來忽略檢查。

```yaml
ignore:
  - *.template.yaml
```

## 參數規則

## 參考資料

[yamllint 文檔](https://yamllint.readthedocs.io/en/stable/#module-yamllint)]
