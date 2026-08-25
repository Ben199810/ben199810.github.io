---
title: "加速團隊開發，使用 Gitlab Package Registry發佈 Private Package"
date: 2026-08-25T15:06:54+08:00
tags: ["Nodejs", "Gitlab"]
draft: false
description: ""
---

## 前言

npm 是 nodejs預設的套件管理工具，龐大的開源社群提供了非常多的模組讓開發人員可以免費下載，加速軟體專案的開發。在實務上如果公司組織內部也有一些共用的模組專案，提供給其他專案能夠統一風格或加快開發的流程。但是一般來說這些共用的模組專案並不會對外開放，通常會將模組存放在公司內部的私有儲存庫，例如: gitlab、github，所以我們會將這些模組稱作私有庫模組。僅限公司內部的其他專案可以下載。

這次會介紹使用 gitlab package registry功能，存放私有套件模組，並提供給其他專案使用。

<!-- prettier-ignore -->
{{< mermaid >}}
flowchart LR
module(module project)
registry(gitlab package registry)
main(main project)

module -->|push| registry -->|install| main
{{< /mermaid >}}

## 如何封裝模組專案

首先第一步，要先將模組專案封裝起來，這樣才可以提供給其他專案做使用。在本機電腦上先克隆模組專案，並進入模組專案的目錄內部。在目錄裡通常可以找到 `package.json`檔案，可以看檔案內會包含什麼內容。

可以看到 common-files模組專案，目前的版本是 `0.2.13`，主要的進入點程式是 `index.js`。因為這個專案的結構簡單沒有使用任何開源社群提供的模組，所以在封裝 package之前，不需要先執行 `npm install`。也不需要執行 `npm run build`，如果你的專案有外部依賴套件而且需要先建構，記得要先執行。

```json
{
  "name": "common-files",
  "version": "0.2.13",
  "main": "index.js",
  "license": "MIT"
}
```

接下來，會先在本機電腦上封裝 package，我們使用 `npm pack`這個指令會將模組專案封裝成一個 `.tgz`的壓縮檔。`--pack-destination` 可以幫助我們將 package輸出到特定的路徑底下。

```shell
npm pack --pack-destination ~
```

封裝的 package名稱會是 name加上 version所以壓縮檔名稱會是 `common-files-0.2.14.tgz`，有了檔案以後，接著我們會克隆主專案，在本機電腦先 install 這個 package來檢查有沒有異常。

## 主專案引用本機電腦模組 package

進入到主專案後，我們需要在 `package.json`的 `dependencies`宣告對模組的使用。

```json
"dependencies": {
  "@game-client/common-files": "file:~/common-files-0.2.14.tgz"
```

完成以後，我們可以使用 `npm install`安裝本地的模組套件了。

這個情境只適用於個人在本機電腦上面模擬私有庫模組套件的使用而已，如果公司內部需要跨單位或者其他專案有需求需要接入這個模組，我們需要將模組套件放到私有的 registry提供內部人員使用。

## gitlab package registry分享模組套件

gitlab 內建了一個私有套件管理庫，可以讓公司的團隊發布、分享和使用各種軟體的模組套件。而這次我們就要將模組套件推送到這裡，提供其他單位或組別的專案可以使用。

推送到 gitlab package registry 會有幾點事項需要注意:

1. 名稱的命名需要使 @{scope}/package-name

   這裡的 @{scope}是指根群組(root group)，舉例來說有一個專案的網址 `https://gitlab.com/my-org/engineering-group/analytics`可以看到這個專案有兩根群組與子群組，而根群組就是 my-org。

   | Project URL                                           | Package Registry in | Scope   | Full package name    |
   | ----------------------------------------------------- | ------------------- | ------- | -------------------- |
   | https://gitlab.com/my-org/engineering-group/analytics | Analytics           | @my-org | @my-org/package-name |

2. package.json新增 publishConfig

   publishConfig用於推送時，告訴 npm管理套件要發布模組到哪裡。

   ```json
    "publishConfig": {
      "@game_client:registry": "https://${gitlab_domain}/api/v4/projects/${projct_id}/packages/npm/"
    }
   ```

   除了在 package.json新增設定的方式以外，也可以用使用 .npmrc寫入 registry的資訊。

   ```txt
    @scope:registry=https://your_domain_name/api/v4/projects/your_project_id/packages/npm/
   ```

   - 替換 @scope為要將套件發佈到的項目的群組
   - 替換 your_domain_name為您的域名
   - 替換 your_project_id為您的項目 ID

3. 需要使用 token進行驗證

   設定好模組套件專案 registry設定資訊後，私有的 registry進行操作時，都會需要身份驗證。來證明你有權限可以存取。一樣可以在 .npmrc新增身份驗證需要的資訊。

   ```txt
    //your_domain_name/api/v4/projects/your_project_id/packages/npm/:_authToken="${NPM_TOKEN}"
   ```

   上面範例提到的 ${NPM_TOKEN}可以是 Personal Access Token，如果在 gitlab CI的流程內，我們也可以使用 CI_JOB_TOKEN 來標準化流程，不使用個人的 Token。

   {{< alert icon="fire" cardColor="#e63946" iconColor="#1d3557" textColor="#f1faee" >}}
   切勿將 GitLab Token(或任何Token)直接硬編碼到.npmrc檔案或任何其他可以提交到儲存庫的檔案中。
   {{< /alert >}}

   配置好權限驗證的檔案以後，可以推送套件到 registry了，執行 `npm publish`會同時封裝與推送。

   ```shell
   npm publish
   ```

   成功推送到 registry以後，可以在 gitlab的 package registry頁面上看到 package已經出現了。

   ![package](/img/posts/gitlab/npm-private-package-publish/push-tgz-package-registry.png)

## 主專案引用 gitlab registry模組 package

前面有提到，存取 gitlab package registry需要經過身份驗證，對於主專案需要存取的這一個行為，我們也需要設定身份驗證的資訊才可以。這裡一樣會使用 .npmrc管理 registry與身份驗證資訊。

```txt
@scope:registry=https://your_domain_name/api/v4/projects/your_project_id/packages/npm/
//your_domain_name/api/v4/projects/your_project_id/packages/npm/:_authToken="${NPM_TOKEN}"
```

接著，可以執行安裝指令下載私有庫套件。

```shell
npm install @{scope}/common-files
```

成功下載以後，可以在 node_modules/ 目錄中看到已經模組專案已經被當作是依賴套件成功安裝，例如圖片中顯示的樣子:

![](/img/posts/gitlab/npm-private-package-publish/node-modules.png)

隨著時間推移，可能會有越來越多版本，如果要查詢目前最新的版本是什麼？可以新查詢 registry上 latest指向的版本。

```shell
npm view @${scope}/common-files@latest version
```

接著看專案目前安裝的版本。

```shell
npm ls @${scope}/common-files --depth=0
```

如果需要更新到最新的版本可以使用下面的更新指令進行版本更新。

```shell
npm install @game_client/common-files@latest
```

## 參考文獻

- [Use npm pack to test your packages locally](https://dev.to/scooperdev/use-npm-pack-to-test-your-packages-locally-486e)
- [Publishing a package by using a CI/CD pipeline](https://archives.docs.gitlab.com/16.6/ee/user/packages/npm_registry/index.html#publishing-a-package-by-using-a-cicd-pipeline)
