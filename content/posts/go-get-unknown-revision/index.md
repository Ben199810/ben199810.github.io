---
title: 'Go Get 出現 "Invalid Version: Unknown Revision" 錯誤 - 排查過程與解決方式'
date: 2026-08-10T15:23:38+08:00
draft: false
tags: ["Go"]
description: "執行 go get 取得私有庫時，出現 Invalid Version: Unknown Revision 錯誤訊息，排查過程與解決方式，包含檢查 go env、git config、git 的歷程以及 git ls-remote 等方式。"
---

執行 `go get` 取得私有庫時，出現以下錯誤訊息：

```text
go: downloading previate.gitlab.com/api/common v0.0.7 go: usersystem/api imports config: previate.gitlab.com/api/common@v0.0.7: reading previate.gitlab.com/api/common/go.mod at revision v0.0.7: git ls-remote -q origin in
```

這個錯誤顯示 go get 取得了一個無效的版本，因為找不到指定的版本 v0.0.7 導致的錯誤。

以下紀錄了排查的過程以及最後解決的方式‼️如果有遇到相同的問題，可以參考以下的排查方式:

## 檢查 go env🔍

檢查 go env，確認 GOPRIVATE 是否有設定私有庫的 domain。設置 GOPRIVATE 可以讓 go get 在存取私有庫時，使用 git 的方式存取，而不會使用 proxy.golang.org。

```bash
go env -w GOPRIVATE=previate.gitlab.com
```

## 檢查 git config🔍

go get 私有庫套件時，預設會使用 HTTPS 的方式存取，會需要輸入使用者名稱與個人存取權杖 (Personal Access Token) 來進行驗證，如果沒有跳出輸入帳號密碼的提示。可以使用 ssh 的方式存取，如果已經有在私有庫配置好 SSH Key，則不需要輸入帳號密碼。

```bash
git config --global url."git@previate.gitlab.com:".insteadOf "https://previate.gitlab.com/"
```

## 檢查 git 的歷程🔍

這行指令可以檢查 go get 在取得私有庫套件時，git 的歷程，並且可以看到 git 在存取私有庫時，是否有出現錯誤訊息。

```bash
GIT_TERMINAL_PROMPT=1 GIT_TRACE=1 go get -x previate.gitlab.com/api/common@v0.0.7
```

可以看到更詳細的錯誤訊息✉️

```text
get "previate.gitlab.com/api/common": found meta tag vcs.metaImport{Prefix:"previate.gitlab.com/api/common", VCS:"git", RepoRoot:"https://previate.gitlab.com/api/common.git"} at //previate.gitlab.com/api/common?go-get=1

go: previate.gitlab.com/api/common@v1.0.35: reading previate.gitlab.com/api/common/go.mod at revision v1.0.35: unknown revision refs/tags/v1.0.35
```

這裡發現 Go 其實已經成功透過 ?go-get=1 解析出私有庫結構，但是在取得指定的版本 v1.0.35 時，出現了 unknown revision。

## 檢查 git ls-remote🔍

檢查共用私有庫的 git ls-remote 是否可以正常存取，並且確認是否有 v0.0.7 這個 tag。

```bash
git ls-remote https://previate.gitlab.com/api/common.git
```

如果可以正常存取，會看到類似以下的輸出：

```text
e1f6c3b8d9f4c3e5e5e refs/tags/v0.0.7
v1f6asdfas2343sfasg refs/tags/v0.0.6
afa1e1f8uw3b89f4c3e refs/tags/v0.0.5
```

## 解決方式✅

上述的問題都檢查過了，最後還是出現 "Invalid Version: Unknown Revision" 的錯誤訊息，最後懷疑可能是 git 的套件出現問題，嘗試更新 git 版本，更新後就可以正常使用 go get 取得私有庫套件。

```bash
brew upgrade git
```

## 感想💭

老實說最後也不知道為什麼會想要去更新 git 版本，因爲已經黔驢技窮了

![](/img/posts/go-get-unknown-revision/memes1.png)

本來只是抱持著姑且一試的心情去嘗試的沒想到就真的好了。不過上面的檢查流程還是很重要，如果可以提前知道問題並解決那就更好了！
