---
title: "規格驅動開發：使用 AI 工具進行協作開發的實踐"
date: 2025-10-26T12:03:58+08:00
draft: false
tags: ["GitHub Copilot","AI 協作開發","規格驅動開發"]
description: "使用 AI 工具進行協作開發的實踐"
---
## 前言📖

在現代軟體開發中，團隊協作是成功的關鍵。隨著人工智慧技術的進步，像 GitHub Copilot 這樣的 AI 工具已經成為開發者的重要助手。本文希望透過規格驅動開發來限制並使團隊在使用 AI 工具進行開發時，能夠有效的避免 AI 工具產生的幻覺以及發散。

## 什麼是規格驅動開發❓

規格驅動開發是以明確的需求和規格，來告訴並規範 AI 工具專注於明確的需求規格作為上下文實踐。過程中可以分成以下規範：

- 憲法（constitution）專案的管理原則和開發指南，這是最高的規範。後面所有的訂定的規範或者任務都必須要遵從憲法。
- 規範（specify）你想要建立什麼？這個步驟會描述需求和使用者故事。
- 計畫（plan）使用你選擇的技術棧或技術堆疊來建立技術實現計畫。
- 任務（task）產生可以執行的任務清單。
- 實作（implement）依照任務清單執行所有的任務建立功能。

### spec-kit💫

spec-kit 是一個開源的工具，可以幫助我們更好地實踐規格驅動開發。它提供了一套標準化的流程和範本，讓團隊能夠更容易地定義和管理規格。

- GitHub Repository: [spec-kit](https://github.com/github/spec-kit)

#### 如何使用 spec-kit❓

1. **安裝**
    首先我們需要將 spec-kit 安裝到我們的開發專案中，使用 `uv` 套件管理工具進行安裝：

    - 永久且一次性的安裝

    ```bash
    uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
    # upgrade
    uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git
    ```

    - 臨時安裝不會永久安裝

    ```bash
    uvx --from git+https://github.com/github/spec-kit.git specify init <PROJECT_NAME>
    ```

2. **初始化專案**

    使用以下指令來初始化一個新的規格驅動開發專案：

    ```bash
    specify init <PROJECT_NAME>
    ```

    如果已經有一個已經存在的專案，可以使用以下指令來初始化：

    ```bash
    cd <EXISTING_PROJECT_DIRECTORY>
    specify init --here
    ```

#### 目錄結構📂

初始化完成後，專案目錄結構會產生以下的目錄和檔案，方便我們進行規格驅動開發：

- prompts AI 工具使用的提示詞範本
- copilot-instructions.md 一開始進行初始化時可以選擇使用的 AI，這邊我選擇的是 GitHub Copilot
- constitution.md 專案憲法
- scripts 生成規格驅動開發需要的文件腳本
- templates 生成規格驅動開發需要的文件範本

```text
.
├── .github
│   ├── prompts # AI 工具使用的提示詞範本
│   │   ├── analyze.prompt.md
│   │   ├── clarify.prompt.md
│   │   ├── constitution.prompt.md
│   │   ...
│   └── copilot-instructions.md # 一開始進行初始化時可以選擇使用的 AI 工具
├── .specify
│   ├── memory
│   │   └── constitution.md # 專案憲法
│   ├── scripts
│   │   └── bash # 生成規格驅動開發需要的文件腳本
│   │       ├── check-prerequisites.sh
│   │       ...
│   └── templates # 生成規格驅動開發需要的文件範本
│       ├── agent-file-template.md
│       ├── plan-template.md
│       ...
...
```

#### 使用 spec-kit 指令與 AI 進行交互🤖

當我們已經完成了 spec-kit 在專案中的初始化後，我們就可以使用 spec-kit 提供的指令來與 AI 工具進行交互，並且根據我們的需求來生成相應的規格和任務。

| 指令 | 說明 |
|------|------|
| /speckit.constitution | 產生或更新專案憲法 |
| /speckit.specify | 產生或更新需求規格(使用者故事) |
| /speckit.plan | 產生或更新技術棧或技術堆疊的實現計畫 |
| /speckit.task | 依照 plan 計畫，產生或更新任務清單 |
| /speckit.implement | 執行所有任務，實現目標功能 |

**提升品質或驗證的指令**📈

這些指令是可選的，不一定要使用，但可以幫助我們提升規格和任務的品質：

| 指令 | 說明 |
|------|------|
| /speckit.clarify | 澄清規格或任務中的不明確之處(建議在 speckit.plan 之前使用) |
| /speckit.analyze | 分析任務執行時元件之間的相依性以及風險(建議在 speckit.task 之後使用，在 speckit.implement 之前使用) |
| /speckit.checklist | 產生一個自訂的檢查清單來驗證規格或任務的完整性(類似單元測試的概念) |

#### 範例流程🚀

經過上面的講解，我們可以看到使用 spec-kit 來進行規格驅動開發的流程是非常清晰且有條理的。github 專案上有詳細的範例可以參考：[spec-kit example](https://github.com/github/spec-kit?tab=readme-ov-file#-detailed-process)

這個範例非常的詳細，包括了每個步驟的說明以及如何使用 spec-kit 指令來與 AI 工具進行交互。建議大家可以參考這個範例來更好地理解規格驅動開發的流程。

## 結論🎯

透過規格驅動開發並且在訂定專案憲法（constitution）的前提下，能夠更有效的避免 AI 工具產生的幻覺以及發散。提供給團隊在使用 AI 工具進行協作開發時，一個清晰且有條理的流程，提升開發效率和品質。

## 參考文獻📚

- [Spec-Driven Development：讓 AI 真正理解你想要什麼](https://ithelp.ithome.com.tw/articles/10378588)
