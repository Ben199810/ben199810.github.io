---
title: "Commitlint Tool"
date: 2026-05-27T14:50:41+08:00
draft: true
description: ""
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
const typeEnum [
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
  extends: ['@commitlint/config-conventional'],
}
```

## 參考文獻📚

- [專業協作開發：使用 Commitlint 規範你的提交訊息](https://notes.boshkuo.com/docs/NodeJS/pkgs/commitlint)
