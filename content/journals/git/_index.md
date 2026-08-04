---
title: "Git 基礎教學：從入門到實務應用"
date: 2026-03-23T09:34:09+08:00
draft: false
tags: ["Git", "版本控制", "軟體開發"]
description: "Git 是一個分布式版本控制系統，廣泛應用於軟體開發中。本文將介紹 Git 的基本概念和使用方法，幫助初學者快速上手 Git，並且在實務中有效地使用 Git 來管理代碼和協作開發。"
---
## 前言🔖

步入職場後，發現 Git 是一個不可或缺的工具。但是發現對於周遭的同事來說，很多人對 Git 的理解都停留在表面，甚至有些人連基本的 commit、push 都不太清楚。這讓我覺得有必要寫一篇文章來介紹 Git 的基本概念和使用方法，希望能幫助到那些剛接觸 Git 的人。

以下的教學是作者在工作中實際使用 Git 的經驗總結，並且參考了官方文檔和一些優秀的教程。希望能夠幫助到大家更好地理解和使用 Git。

## Git 是什麼？🤔

簡單來說，Git 是一個分布式版本控制系統。它可以幫助我們管理和跟蹤代碼的變化，讓我們能夠輕鬆地協作開發。Git 的核心概念包括：

- **Repository（倉庫）**：用來存儲代碼和版本歷史的地方。可以是本地的，也可以是遠程的。
- **Commit（提交）**：一次對代碼的修改，包含了修改的內容和相關的元數據（如作者、時間等）。
- **Branch（分支）**：用來實現並行開發的機制，可以讓不同的開發者在不同的分支上工作，最後再合併到主分支。
- **Merge（合併）**：將一個分支的修改合併到另一個分支的過程。
- **Pull Request（拉取請求）**：在遠程倉庫中，當你完成了一個功能的開發，想要將它合併到主分支時，可以創建一個 Pull Request，讓其他人來審核你的代碼。

上述的這幾個功能是在日常開發中與工作實務中最常用到的 Git 功能，當然 Git 還有很多其他的功能和概念，這裡就不一一介紹了。

## Git 的基本使用方法🚀

### 1. 初始化倉庫

如果今天管理者分配了一個新的專案給你，你需要在公司的 Git 服務（如 GitHub、GitLab 等）上創建一個新的倉庫，要如何初始化這個倉庫呢？你可以使用以下命令：

```bash
git init
```

這個命令會在當前目錄下創建一個新的 Git 倉庫，並且會生成一個 `.git` 的隱藏文件夾，這個文件夾用來存儲 Git 的相關信息。

如果先在 Git 服務上創建了倉庫，然後想要將本地的代碼推送到遠程倉庫，可以使用以下命令：

```bash
git remote add origin <遠程倉庫的URL>
git push -u origin master # 或者 main，取決於你的主分支名稱
```

這樣一來，你就成功地將本地的代碼推送到了遠程倉庫，並且設置了 `origin` 作為默認的遠程倉庫，接下來就可以開始提交程式碼了。

### 2. 建立分支

在多人協作開發中，建立分支是一個非常重要的步驟。分支可以讓不同的開發者在不同的分支上工作，避免了直接在主分支上修改代碼可能帶來的風險。

可以從圖片中看到，今天要為產品開發一個新的功能，為了不影響主分支的穩定性，我們可以創建一個新的分支來開發這個功能。使用以下命令來創建和切換到新的分支：

```bash
git checkout -b feature/new-feature
```

切換分支以後，你就可以在這個分支上進行開發了。當你完成了這個功能的開發，並且測試通過了，就可以將這個分支合併回主分支了。

以上是比較簡單的說明，實務上還是要依照各家公司的流程來進行，例如: 功能分支需要經過 code review 才能合併到主分支，或者是需要先將功能分支合併到 develop 分支，再由 develop 分支合併到主分支等等，這些都是公司內部的流程規定，需要根據實際情況來操作。

{{< mermaid >}}
---

title: "Git 分支示意圖"
---

gitGraph
  commit
  commit
  branch feature/new-feature
  checkout feature/new-feature
  commit
  commit
  checkout main
  merge feature/new-feature
{{< /mermaid >}}

### 3. 提交程式碼

當你在功能分支上完成了開發，並且測試通過了，就可以將這些修改提交到 Git 中了。使用以下命令來提交程式碼：

```bash
git add . # 將所有修改的文件添加到暫存區
git commit -m "feat: add new feature" # 提交修改，並且添加提交信息
```

上述指令完成後，在本機電腦上就會有一個新的提交，這個提交包含了你剛才修改的內容和提交信息。接下來，你可以將這個提交推送到遠程倉庫中，讓其他人也能看到你的修改：

```bash
git push origin feature/new-feature
```

### 4. 更新主分支 & Rebase

上面已經學習到了，透過創建分支來開發新的功能，這樣可以避免直接在主分支上修改代碼帶來的風險。但是在實際開發中，主分支可能會不斷地有新的提交，這時候我們需要將主分支的最新變化合併到我們的功能分支中，以確保我們的功能分支是基於最新的主分支進行開發的。

這點非常重要，建議，固定時間例如每天早上班的第一件事就是將主分支的最新變化合併到自己的功能分支中，這樣可以避免在後續開發中出現太多的衝突。

有兩種常見的方法可以將主分支的最新變化合併到功能分支中：

1. **Merge（合併）**：使用 `git merge` 命令將主分支合併到功能分支中。這種方法會保留主分支的提交歷史，並且會產生一個新的合併提交。

```bash
git checkout feature/new-feature
git merge main
```

可以看到，這樣會在功能分支上產生一個新的合併提交，這個提交會包含主分支的最新變化。

{{< mermaid >}}
---

title: "Git Merge 示意圖"
---

gitGraph
  commit
  commit
  branch feature/new-feature
  checkout feature/new-feature
  commit
  commit
  checkout main
  commit
  checkout feature/new-feature
  merge main
{{< /mermaid >}}

1. **Rebase（變基）**：使用 `git rebase` 命令將功能分支的提交重新應用到主分支的最新提交之上。這種方法會改變功能分支的提交歷史，使其看起來像是直接從主分支的最新提交開始的。

```bash
git checkout feature/new-feature
git rebase main
```

這也是我在工作上比較常用的方法，因為它可以保持提交歷史的整潔，讓我們的功能分支看起來像是直接從主分支的最新提交開始的。以下會展示一下 Rebase 之前和 Rebase 之後的示意圖，讓大家更清楚地理解 Rebase 的作用。

{{< mermaid >}}
---

title: "Git Rebase 示意圖，Rebase 之前"
---

gitGraph
  commit id: "init"
  commit id: "update: commit 1"
  branch feature/new-feature
  checkout feature/new-feature
  commit id: "feature: commit 2"
  commit id: "feature: commit 3"
  checkout main
  commit id: "update: commit 4"
{{< /mermaid >}}

{{< mermaid >}}
---

title: "Git Rebase 示意圖，Rebase 之後"
---

gitGraph
  commit id: "init"
  commit id: "update: commit 1"
  commit id: "update: commit 4"
  branch feature/new-feature
  checkout feature/new-feature
  commit id: "feature: commit 2"
  commit id: "feature: commit 3"
{{< /mermaid >}}

可以看到，Rebase 之前，功能分支的提交歷史是基於主分支的第一個提交（update: commit 1）開始的，而 Rebase 之後，功能分支的提交歷史是基於主分支的最新提交（update: commit 4）開始的。這樣就保持了提交歷史的整潔，讓我們的功能分支看起來像是直接從主分支的最新提交開始的。

### 5. 壓縮提交（Squash Commits）

這也是我在工作中比較常用的一個功能，當我們在功能分支上進行開發的時候，可能會有很多的提交，某些提交可能是一些小的修改或者是一些無意義的提交，這時候我們可以使用 `git rebase -i` 命令來壓縮這些提交，讓提交歷史看起來更整潔。

作者在工作上常常看到很多開發者的功能分支上有很多的提交，大量且無意義的提交會讓提交歷史變得非常混亂。也會使團隊的運維變的非常麻煩，因為在進行回滾或者是查看提交歷史的時候，會被這些無意義的提交所干擾，難以找到真正有用的提交。所以建議大家在開發完成後，或者是在提交之前，先使用 `git rebase -i` 命令來壓縮這些提交，讓提交歷史看起來更整潔。

```bash
git checkout feature/new-feature
git rebase -i HEAD~n # n 是你想要壓縮的提交的數量
```

這個命令會打開一個交互式的界面，讓你選擇要壓縮的提交。你可以將要壓縮的提交標記為 `squash`，然後保存並退出，Git 就會將這些提交壓縮成一個提交。
這樣就可以讓提交歷史看起來更整潔，讓團隊的運維變得更簡單。

{{< mermaid >}}
---

title: "Git Rebase -i 示意圖，Squash Commits 之前"
---

gitGraph
  commit id: "init"
  commit id: "update: commit 1"
  branch feature/new-feature
  checkout feature/new-feature
  commit id: "feature: commit 2"
  commit id: "test: commit 3"
  commit id: "fix: commit 4"
{{< /mermaid >}}

{{< mermaid >}}
---

title: "Git Rebase -i 示意圖，Squash Commits 之後"
---

gitGraph
  commit id: "init"
  commit id: "update: commit 1"
  branch feature/new-feature
  checkout feature/new-feature
  commit id: "feature: commit 2 ~ commit 4"
{{< /mermaid >}}

從上面的示意圖可以看到，Squash Commits 之前，功能分支上有三個提交（feature: commit 2、test: commit 3、fix: commit 4），這些提交可能是一些小的修改或者是一些無意義的提交。Squash Commits 之後，這三個提交被壓縮成了一個提交（feature: commit 2 ~ commit 4），這樣就讓提交歷史看起來更整潔了。

### 6. 暫存修改（Stash）

git stash 是一個非常有用的功能，當你在開發過程中，突然需要切換到另一個分支去處理一些緊急的問題，但是本機電腦上的修改還沒有提交，這時候你就可以使用 git stash 命令來暫存這些修改，讓你可以切換到另一個分支去處理緊急的問題。

```bash
git stash # 暫存工作區的修改
git stash -u # 暫存工作區的修改和未追蹤的文件
```

當你處理完緊急的問題，想要回到之前的分支繼續開發的時候，你可以使用以下命令來恢復之前暫存的修改：

```bash
git stash pop # 恢復暫存的修改，並且從暫存列表中刪除這個暫存
git stash apply # 恢復暫存的修改，但不會從暫存列表中刪除這個暫存
```

## Git Flow 工作流程🌊

Git Flow 是什麼？為什麼我們需要 Git Flow？

Git Flow 是一種基於 Git 的分支管理模型，它定義了一套嚴格的分支結構和工作流程，讓團隊能夠更好地協作開發。Git Flow 的主要分支包括：

- **master（主分支）**：用來存儲生產環境的代碼，這個分支上的代碼應該是穩定的，可以隨時部署到生產環境中。
- **develop（開發分支）**：用來存儲開發中的代碼，這個分支上的代碼可能不穩定，只有當開發完成並且測試通過了，才會將這些修改合併到 master 分支中。
- **feature（功能分支）**：用來開發新的功能的分支，這些分支是從 develop 分支上創建的，當功能開發完成並且測試通過了，就會將這些修改合併到 develop 分支中。
- **release（發布分支）**：用來準備發布的分支，這些分支是從 develop 分支上創建的，當發布準備完成並且測試通過了，就會將這些修改合併到 master 分支中，並且打上發布的標籤。
- **hotfix（熱修復分支）**：用來修復生產環境中的緊急問題的分支，這些分支是從 master 分支上創建的，當修復完成並且測試通過了，就會將這些修改合併到 master 分支中，並且打上修復的標籤。

Git Flow 的工作流程如下：

- 開發新的功能：從 develop 分支上創建一個新的 feature 分支，進行功能開發，當功能開發完成並且測試通過了，就會將這些修改合併到 develop 分支中。

{{< mermaid >}}
---

title: "Git Flow 工作流程，開發新的功能"
---

gitGraph
  commit id: "init"
  commit id: "update: commit 1"
  branch develop
  checkout develop
  commit id: "develop: commit 2"
  branch feature/new-feature
  checkout feature/new-feature
  commit id: "feature: commit 3"
  commit id: "feature: commit 4"
  checkout develop
  merge feature/new-feature
{{< /mermaid >}}

- 準備發布：從 develop 分支上創建一個新的 release 分支，進行發布準備，當發布準備完成並且測試通過了，就會將這些修改合併到 main 分支中，並且打上發布的標籤。

{{< mermaid >}}
---

title: "Git Flow 工作流程，準備發布"
---

gitGraph
  commit id: "init"
  commit id: "update: commit 1"
  branch develop
  checkout develop
  commit id: "develop: commit 2"
  branch feature/new-feature
  checkout feature/new-feature
  commit id: "feature: commit 3"
  commit id: "feature: commit 4"
  checkout develop
  merge feature/new-feature
  branch release/v1.0
  checkout release/v1.0
  checkout main
  merge release/v1.0
{{< /mermaid >}}

- 修復緊急問題：從 main 分支上創建一個新的 hotfix 分支，進行緊急問題的修復，當修復完成並且測試通過了，就會將這些修改合併到 main 分支中，並且打上修復的標籤。

{{< mermaid >}}
---

title: "Git Flow 工作流程，修復緊急問題"
---

gitGraph
  commit id: "init"
  commit id: "update: commit 1"
  branch hotfix/bug-fix
  checkout hotfix/bug-fix
  commit id: "hotfix: commit 3"
  checkout main
  merge hotfix/bug-fix
{{< /mermaid >}}

上述只是簡單的介紹了 Git Flow 的工作流程，實際上在不同的團隊中，Git Flow 的工作流程可能會有所不同，具體的流程需要根據團隊的實際情況來制定。

例如: 使用分支區分各環境部署，main 分支用來部署生產環境，develop 分支用來部署開發環境，qa 分支用來部署測試環境等等，這些都是團隊內部的流程規定，需要根據實際情況來操作。

{{< mermaid >}}
---

title: "Git Flow 工作流程，分支區分各環境部署"
---

gitGraph
  commit id: "init"
  commit id: "update: commit 1"
  branch develop
  branch qa
  branch feature/new-feature
  checkout feature/new-feature
  commit id: "feature: commit 2"
  commit id: "feature: commit 3"
  checkout develop
  merge feature/new-feature
  checkout qa
  merge feature/new-feature
  checkout main
  merge feature/new-feature
{{< /mermaid >}}

上述的示意圖展示了 Git Flow 工作流程中，分支區分各環境部署的情況。也是目前作者在工作中最常使用的流程，因為通常 SRE 會需要管理多個環境的部署，這樣就可以通過分支來區分不同環境的部署，讓 SRE 的工作變得更簡單。

## 結語🎉

Git 是一個非常強大的版本控制系統，學習 Git 的基本概念和使用方法是每個軟體開發者必須掌握的技能。希望這篇文章能夠幫助到那些剛接觸 Git 的人，讓他們能夠快速上手 Git，並且在實務中有效地使用 Git 來管理代碼和協作開發。

希望每個人都能有一個愉快的 Git 旅程，讓我們在軟體開發的道路上越走越遠！

## 參考文獻📚

- [學習 Git 分支](https://learngitbranching.js.org/?locale=zh_TW)
- [連猴子都能懂的 Git 入門指南](https://web.archive.org/web/20230518032601/https://backlog.com/git-tutorial/tw/)
