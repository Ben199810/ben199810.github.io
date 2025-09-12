---
title: "GitHub Copilot 實用新功能(version 1.104)"
date: 2025-09-12T09:16:17+08:00
draft: false
description: ""
---
## 自動模型選擇功能

github copilot agent 推出自動選擇模型功能，VSCode 會自動選擇一個模型，確保獲得最佳效能並避免速率限制。

自動模型選擇功能會在 Claude Sonnet 4、GPT-5、GPT-5 mini、GPT-4.1 和 Gemini Pro 2.5 之間進行選擇。除非你停用這些模型的存取權限。

自動模型選擇功能會提供 10% 的折扣。可以將滑鼠懸停在聊天視圖中來查看所選模型和模型乘數。

## 確認敏感文件的編輯

當你嘗試編輯敏感文件時，GitHub Copilot 會顯示一個確認對話框，讓你確認是否要繼續編輯。

![確認編輯對話框](/img/github-copilot/20250911-release/confirm-sensitive-file-edit.png)

在代理模式下，代理可以自主編輯您工作區中的文件。這可能包括意外或惡意修改或刪除重要檔案（例如設定檔），這可能會對您的電腦造成直接的負面影響。

如果要更改設定的話，可以在 `設定` 中搜尋 `chat.tools.edits.autoApprove`。

![敏感文件編輯設定](/img/github-copilot/20250911-release/confirm-sensitive-file-edit-setting.png)

## 設定 agentMDFile(實驗性功能)

可以在 `設定` 中搜尋 `chat.useAgentsMdFile` 來啟用這個實驗性功能。

AGENTS.md 可以讓你提供 agent 上下文資訊或指令。

簡單來說 README.md 是提供給人類閱讀的，而 AGENTS.md 是提供給 AI agent 閱讀的。所以你必須在 AGENTS.md 中提供更詳細的資訊。例如：如何建立專案、執行什麼類型的測試、希望遵循的程式碼風格指南等。

## 改善了已更改文件的體驗

- 在聊天視圖中已更改的文件預設會摺疊起來，以便為聊天對話提供更多空間。在折疊狀態下，您仍然可以看到已更改檔案的數量以及新增或刪除的行數。
- 當您保留或接受建議的變更時，該檔案將從檔案變更清單中刪除。
- 當您使用原始碼控制視圖暫存或提交文件時，它會自動接受建議的文件變更。
- 現在會顯示清單中每個項目的每個檔案的變更（新增或刪除的行）。

## 參考

- [August 2025 (version 1.104)](https://code.visualstudio.com/updates/v1_104)
