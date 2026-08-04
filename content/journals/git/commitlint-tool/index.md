---
title: "使用 commitlint 工具規範提交訊息格式"
date: 2026-05-27T14:50:41+08:00
draft: false
description: "在專業協作開發中，使用 commitlint 工具來規範提交訊息的格式是非常重要的。這不僅有助於提高代碼的可讀性，還能促進團隊協作和版本控制的管理。本文將介紹如何使用 commitlint 工具來規範提交訊息格式，以及一些常用的規則和插件配置。"
tags: ["git", "commitlint", "工具", "提交訊息", "規範"]
---

## 前言🔖

上一篇文章提到了專案中使用 commitlint 工具來規範 commit message 的格式，確保團隊成員在提交代碼時遵循統一的規範。這不僅有助於提高代碼的可讀性，還能促進團隊協作和版本控制的管理。

為什麼需要導入 Lint 工具?因為人類是有惰性的😩

就算有文件規範了提交訊息的格式，但如果沒有工具來強制執行，團隊成員可能會忽略這些規範，導致提交訊息不一致，影響代碼庫的整潔和可維護性

## 如何使用 commitlint 工具？

首先，我們需要安裝 commitlint 以及相關的配置套件：

```bash
yarn add --dev @commitlint/{config-conventional,cli}
# 或者使用 npm
npm install --save-dev @commitlint/{config-conventional,cli}

echo "export default { extends: ['@commitlint/config-conventional'] };" > commitlint.config.js
```

接著，安裝 husky 來在 git commit 時自動執行 commitlint：

```bash
yarn add --dev husky
# 或者使用 npm
npm install --save-dev husky
```

### 基礎配置⚙️

安裝完套件後，我們需要進行一些基礎配置，使 commitlint 和 husky 能夠正常運作。

1. 配置 commitlint.config.js：

```javascript
module.exports = {
  extends: ['@commitlint/config-conventional'],
};
```

這個配置文件告訴 commitlint 使用 @commitlint/config-conventional 的規則來檢查提交訊息。

1. 配置 husky：

```bash
yarn husky init
```

這個命令會在專案根目錄下創建一個 .husky 目錄

接著，配置 commit-msg hook，使其在提交訊息時自動檢查訊息格式：

```bash
echo "yarn commitlint --edit \$1" > .husky/commit-msg
```

### 常用 Rules 規則

commitlint 允許我們可以自定義規則來檢查提交訊息的格式。以下是作者常用的一些規則：

```javascript
const typeEnum = [
  "feat", // 新功能/修改功能
  "fix", // 修復錯誤
  "docs", // 文檔變更
  "style", // 不影響代碼含義的變更 (空格, 格式化, 缺少分號等)
  "refactor", // 代碼重構
  "perf", // 性能優化
  "test", // 添加缺失的測試或更正現有測試
  "build", // 更改構建流程或輔助工具和庫 (例如 webpack, babel, npm)
  "ci", // 更改 CI 配置, 腳本
  "chore", // 對構建過程或輔助工具和庫的更改
  "revert", // 撤銷之前的提交
];

module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "type-enum": [2, "always", typeEnum],
    "subject-format": [2, "always", /^[a-z]+: .+$/i],
    "subject-jira-format": [1, "always", /^[a-z]+: \[.*\] .+$/i],
  },
  parserPreset: {
    parserOpts: {
      headerPattern: /^(\w+): (.+)$/,
      headerCorrespondence: ["type", "subject"],
    },
  },
  plugins: [
    {
      rules: {
        "type-enum": ({ type }) => {
          const isValidType = typeEnum.includes(type);
          return [
            isValidType,
            isValidType
              ? true
              : `輸入的 type '${type}' 不在允許的範圍內: ${typeEnum.join(
                  ", "
                )}。`,
          ];
        },
        "subject-format": (parsed) => {
          const regex = /^[a-z]+: .+$/i;
          const isValidFormat = regex.test(parsed.header);
          return [
            isValidFormat,
            isValidFormat
              ? true
              : `請確保格式為 <type>: <描述>，例如：feat: 新增功能。`,
          ];
        },
        "subject-jira-format": (parsed) => {
          const regex = /^[a-z]+: \[.*\] .+$/i;
          const isJiraFormat = regex.test(parsed.header);
          return [
            isJiraFormat,
            isJiraFormat
              ? true
              : `建議格式為 <type>: [JIRA-ISSUE] <描述>，例如：feat: [JIRA-123] 新增功能。`,
          ];
        },
      },
    },
  ],
};
```

在 rules 中，我們先來解釋陣列內的各個元素代表什麼意思：

- 第一個元素（0, 1, 2）代表規則的嚴重程度，0 表示關閉規則，1 表示警告，2 表示錯誤。
- 第二個元素（"never", "always"）表示規則的觸發條件，"never" 表示不允許使用某些值，"always" 表示必須符合規則。

在這個配置中，我們定義了三個規則：

1. "type-enum": 這個規則檢查提交訊息的 type 是否在允許的範圍內。如果不符合，會返回一個錯誤訊息，提示使用者輸入的 type 不在允許的範圍內。
2. "subject-format": 這個規則檢查提交訊息的格式是否符合 <type>: <描述> 的格式。如果不符合，會返回一個錯誤訊息，提示使用者確保格式正確。
3. "subject-jira-format": 這個規則檢查提交訊息的格式是否符合 <type>: [JIRA-ISSUE] <描述> 的格式。如果不符合，會返回一個警告訊息，建議使用者遵循這個格式。

### plugins 插件

plugins 的作用是用來追加新的自定義規則，與 rules 相輔相成。

## 參考文獻📚

- [專業協作開發：使用 Commitlint 規範你的提交訊息](https://notes.boshkuo.com/docs/NodeJS/pkgs/commitlint)
- [commitlint](https://commitlint.js.org/)
