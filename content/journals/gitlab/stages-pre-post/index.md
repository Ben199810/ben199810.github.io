---
title: "Pipeline 中隱藏的 stages: .pre 和 .post"
date: 2025-07-25T14:06:43+08:00
draft: true
description: ""
---
## 前言

近期維護 CICD 時，發現 GitLab Pipeline 中有兩個隱藏的 stage：`.pre` 和 `.post`。不需要在 `stages` 中明確定義。

```yaml
stages:
  # - .pre # 不需要明確定義
  - test
  - build
  - coverage
  - deploy
  # - .post # 不需要明確定義
```

## 發現問題

Pipeline 執行時，發現 `.post` 跟 `test` 同時執行，這讓我感到困惑。

查閱 GitLab 的文檔後，`.post` 的執行時機是 pipeline 的最後一個階段。

經過調查後發現 needs 關鍵字的使用導致了這個行為。

needs 為空值時，代表 `.post` 就不依賴任何其他 job，這樣的設計邏輯違背了 GitLab 文檔中定義的 `.post` 的行為。

```yaml
job1:
  stage: test
  script:
    - echo "Running tests..."

job2:
  stage: .post
  script:
    - echo "Running post-processing..."
  needs: []
```

## 問題反思

Pipeline 中有 Job 設定 `when: manual` 時， .post stage 會先執行嗎？

這個問題的答案是：不會。

`.post` 在 Pipeline 的最後一個階段執行，但如果有任何 Job 設定為 `when: manual`，那麼 `.post` 會等待這些手動觸發的 Job 完成後才會執行。

![測試 post 執行是否受手動觸發影響](/img/gitlab/pipeline/post-stage-testing.png)

## 結論

同仁希望 `.post` 不會受到 `when: manual` 的影響，正確的做法應該要調整 stage 的名稱，避免使用 `.post`。

並且依照 stage 的執行順序來設計 Job 的依賴關係。例如 `coverage` stage 有 `when: manual` 參數會影響 `rebase` stage 自動執行，所以應該在 `coverage` stage 前執行 `rebase` stage。

而不是將 `rebase` stage 設定為 `.post`，並設置 `needs: []`。

## 參考資料

[stage: .post](https://docs.gitlab.com/ci/yaml/#stage-post)
