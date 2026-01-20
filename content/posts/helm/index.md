---
title: "Kubernetes 管理工具 Helm"
date: 2025-08-19T16:29:36+08:00
draft: false
description: ""
---
## 介紹

Helm 是 Kubernetes 的一個套件管理工具，可以用來簡化應用程式的部署和管理。它使用稱為 Chart 的包裝格式來定義應用程式的各種資源，並提供了一個簡單的命令列介面來安裝、升級和管理這些應用程式。

## 函數

Helm 提供了一些內建函數，可以在 Chart 的模板中使用。這些函數可以用來處理字串、數字、日期等資料類型，並提供了一些常用的功能，可以幫助開發者更方便地編寫和維護 Helm Chart。

### quote

將字符串使用雙引號包裹起來。

⭐️ `sqoute` 表示單引號。

```yaml
userName: User1
```

```yaml
{{ .Values.userName | quote }}
```

得到結果: "User1"

```yaml
{{ .Values.userName | squote }}
```

得到結果: 'User1'

### replace

字串替換。

```yaml
"I Am Henry VIII" | replace " " "-"
```

得到結果: I-Am-Henry-VIII

### dict

傳遞 `key` 和 `value` 來創建一個 `map`。

```yaml
{{ $myDict := dict "key1" "value1" "key2" "value2" }}
```

得到結果:

```yaml
{
  "key1": "value1",
  "key2": "value2"
}
```

### fromYaml

將 YAML 字串轉換為 Object。

filePath: yamls/person.yaml

```yaml
name: Bob
age: 25
hobbies:
  - hiking
  - fishing
  - cooking
```

```yaml
{{- $person := .Files.Get "yamls/person.yaml" | fromYaml }}
```

得到結果:

```json
{
  "name": "Bob",
  "age": 25,
  "hobbies": [
    "hiking",
    "fishing",
    "cooking"
  ]
}
```

### merge, mergeOverwrite

⚠️ 注意目標 `dst` 優先

```yaml
dst:
  default: default
  overwrite: me
  key: true

src:
  overwrite: overwritten
  key: false
```

```yaml
{{- $newdict := merge .Values.dst .Values.src }}
```

得到結果:

```yaml
newdict:
  default: default
  overwrite: me
  key: true
```

如果要以 `src` 為優先，可以使用 `mergeOverwrite` 函數。

```yaml
{{- $newdict := mergeOverwrite .Values.dst .Values.src }}
```

得到結果:

```yaml
newdict:
  default: default
  overwrite: overwritten
  key: false
```

### omit

類似 `pick`，用於從 map 中排除指定的 key。

```yaml
volumeMounts:
  - name: my-volume
    mountPath: /data
    claimName: my-pvc
```

```yaml
{{- range $mount := .volumeMounts }}
  {{- $cleanMount := omit $mount "claimName" }}
{{- end }}
```

得到結果:

```yaml
volumeMounts:
  - name: my-volume
    mountPath: /data
```

### append

在已有陣列中追加一個元素，建立一個新的陣列。

```yaml
myArray:
  - element1
  - element2
  - element3
```

```yaml
{{- $newArray := append .Values.myArray "newElement" }}
```

得到結果:

```yaml
newArray:
  - element1
  - element2
  - element3
  - newElement
```

## 參考資料

[模板函数列表](https://helm.sh/zh/docs/chart_template_guide/function_list/)
