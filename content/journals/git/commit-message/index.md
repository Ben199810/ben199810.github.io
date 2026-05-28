---
title: "Git Commit Message 的撰寫規範與工具推薦"
date: 2026-05-25T17:16:45+08:00
draft: false
description: "在軟體過程開發中，良好的 Git Commit 規範是維護專案歷史清晰、協作順暢的關鍵。本文將介紹如何撰寫優質的 Git Commit Message，並推薦實用工具幫助團隊遵守規範。"
tags: ["Git", "Commit Message", "Conventional Commits", "開發規範", "工具推薦"]
---
## 前言🔖

在軟體過程開發中，良好的 Git Commit 規範是維護專案歷史清晰、協作順暢的關鍵。想像一下，如果每次提交都像寫日記一樣，清楚描述改動內容和原因，未來回顧時就能輕鬆理解每次變更的背景。

## 如何撰寫優質的 Git Commit Message？

在團隊開發中，常常會遇到提交訊息不清晰。會有一大堆的 "fix bug"、"update code" 這類模糊的訊息，讓人無法快速了解改動的內容和目的。為了改善這個問題，我們可以遵循 `Conventional Commits` 的規範，這是一套簡單而強大的提交訊息格式，能夠幫助我們更好地管理專案歷史。

### Conventional Commits 的基本格式

Conventional Commit 的格式其實很簡單，看起來像這樣：

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

讓我們來分解一下每個部分的用途：

1. type(commit 類型)：描述這次 Commit 的性質。常見的類型有：
   - feat: 新功能
   - fix: 修復 bug
   - docs: 文件變更
   - style: 代碼格式（不影響功能）
   - refactor: 代碼重構（既不是新增功能也不是修復 bug）
   - test: 添加測試
   - chore: 其他修改（例如建置流程、工具等）
   - revert: 回退之前的提交

   也可以根據團隊需求自定義其他類型，比如説在 SRE 團隊中，我們還有定義其他的類型，例如：
     - perf: 性能優化
     - build: 更改構建流程或輔助工具和庫 (例如 webpack, babel, npm)
     - ci: 持續集成相關的更改
     - cd: 持續部署相關的更改
2. scope(影響範圍 可選)：描述這次 Commit 影響的範圍，例如模組名稱、功能區域等。如果影響的範圍明確建議可以加上，可以讓訊息更具體。
3. description(簡短描述)：簡要描述這次 Commit 的內容，應該是一句話，清晰明了地說明改動的目的。保持在 50 字以內。
4. body(詳細描述 可選)：如果需要，可以在這裡提供更詳細的說明，解釋為什麼要做這些改動，以及改動的具體內容。
5. footer(附註 可選)：可以用來關聯 issue 或 pull request，例如：

   ```text
   BREAKING CHANGE: 改變了 API 的回傳結構
   Resolves #123
   ```

### 實踐範例

1. 新增功能提交

    ```text
    feat(profile): add user profile page
    ```

2. Bug 修復提交

    ```text
    fix(auth): resolve login issue when using special characters in password
    ```

3. Breaking Change

    ```text
     feat(api): change user endpoint response format

     BREAKING CHANGE: 改變了 API 的回傳結構，請更新前端代碼以適應新的格式
    ```

4. 文件變更提交

    ```text
    docs(readme): update installation instructions
    ```

5. 退回某次提交

    ```text
    revert: feat(profile): add user profile page

    This reverts commit abcdef1234567890.
    ```

## 實用工具推薦

當然，撰寫團隊的 Git Commit 規範只是第一步，實際上在推動團隊遵守這些規範時，還是會遇到一些挑戰。

接續的文章段落會延續介紹作者有使用的工具，幫助團隊更好地遵守 Git Commit 規範。

### Commitlint

- 功能：Commitlint 是一款校驗工具，用來檢查你的 Commit Message 是否符合規範，避免提交不合規的訊息。
- 特色：可整合到 CI/CD 流程中，自動化檢查提交訊息，支援自定義規則，適應不同團隊的需求。

### Husky

- 功能：Husky 是一款 Git hooks 工具，可以在提交前自動執行指定的腳本，例如 Commitlint 的檢查。
- 特色：配合 Commitlint 使用，實現提交訊息的本地校驗。可用於其他操作，如執行測試、格式化程式碼等，擴展性強。

如果想要在專案中引入這些工具，下一篇文章將會介紹如何安裝和配置 Commitlint 和 Husky，讓你的團隊能夠輕鬆遵守 Git Commit 規範。

{{< article link="/journals/git/commitlint-tool/" showSummary=true compactSummary=true >}}

## 參考文獻📚

- [Git Commit Message 這樣寫會更好，替專案引入規範與範例](https://ithelp.ithome.com.tw/articles/10228738)
- [Conventional Commits 的實踐指南：寫出乾淨的提交訊息](https://notes.boshkuo.com/docs/DevTools/Git/conventional-commits)
