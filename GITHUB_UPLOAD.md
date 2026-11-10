# GitHub上传准备 / GitHub publishing preparation

目标仓库 / Target: https://github.com/hahahayasahiro/883-PROJECT

仓库为公开仓库。应用目录 `smartcampus` 作为仓库根目录；源码、虚构示例、汇报材料及使用说明书可以随仓库分发。本机密钥、业务数据库、备份、虚拟环境、缓存和中间录像均排除。没有另行选择开源许可证；公开可访问不等于已经声明开源授权。

The target is public. The application directory is the repository root. Source, fictional examples, presentation materials and the manual are included. Private configuration, local records/backups, environments, caches and intermediate recordings are excluded. No open-source licence has been selected for the team.

网络状态（11月10日检查）：GitHub接口可以读取仓库并确认写权限，但本机Git直连先后出现连接重置及无法连接443端口。实际上传前先恢复Git网络连接，运行 `git ls-remote origin` 确认可访问。该问题发生在网络连接阶段，尚未验证Git推送登录；不能将接口权限检查等同于本机Git推送已成功。

Network status: the GitHub connector can read the repository and confirms write permission, but local Git HTTPS requests encountered a reset and a port-443 connection failure. Restore Git connectivity and check `git ls-remote origin` before publishing. Git push authentication has not been exercised; connector access is not proof of a successful local Git push.

## 已准备 / Prepared

- `main` 作为主分支，`origin` 指向上述仓库；本地提交记录可用 `git log -1 --oneline` 检查。
- 六个模块分支按 [CONTRIBUTING.md](CONTRIBUTING.md) 分配；分支名称不代表相应成员已经提交了独立工作。
- `.gitignore`、`.gitattributes`、PR模板和Windows/Python 3.12自动检查已提供。
- 原提案副本位于 `docs/proposals`，当前汇报入口位于 [交付索引](deliverables/README.md)。
- 当前检查证据与未完成项见 [完整性检查](deliverables/COMPLETENESS_REVIEW.md)。

## 上传前复核 / Before publishing

在本目录运行；`git`需已安装。不要上传上一级整个课程文件夹，也不要拖入 `.env`、`data` 或旧交付压缩包。

Run in this directory with Git installed. Do not upload the entire parent coursework folder, `.env`, `data`, or old delivery archives.

```powershell
git status --short
git remote -v
.\.venv\Scripts\python.exe tools/check-readiness.py
.\.venv\Scripts\python.exe -m pytest -q
```

初次发布前确认没有新增或修改的文件未提交。若有组员新改动，先审核并提交相应文件；不要强制推送。

Ensure the reviewed changes are committed. Review and commit any subsequent team changes before publishing; do not force-push.

## 发布命令 / Publish commands

以下操作会实际上传，准备阶段不会自动执行。Git可能打开GitHub登录窗口，使用有仓库写权限的账号登录；不要把API密钥当成GitHub密码。

These commands actually publish the prepared local commits and are not run merely to prepare the repository. Git may ask you to sign in to a GitHub account with write permission. The DeepSeek API key is not a GitHub password.

```powershell
git push -u origin main
git push origin module/assistant module/learning module/facilities module/maintenance module/reviews module/applications
```

若远程已经被组员提交了新内容，停止首次推送流程并先获取、检查和合并；不要使用 `--force` 覆盖对方记录。网页上确认README、六个模块文件、PPT、说明书与提案可见，然后检查Actions结果。自动检查首次运行尚不能在准备阶段声称已通过。

If a teammate has added remote history, fetch and review it before merging; never overwrite it with a forced initial push. After publishing, check the README, modules, slides, manual, proposals and Actions results. Local checks do not establish that GitHub Actions has run successfully.

## 组员接手 / Teammate setup

```powershell
git clone https://github.com/hahahayasahiro/883-PROJECT.git
cd 883-PROJECT
powershell -ExecutionPolicy Bypass -File .\setup.ps1
.\start.cmd
```

首次安装生成虚构种子数据，不包含本机演示历史。需要AI的组员在自己的 `.env` 中配置密钥。各成员从对应模块分支开发，通过PR合并至main。GitHub上传与Moodle作业提交是两个独立步骤。

A fresh installation creates fictional seed data and does not copy this machine's demo history. Configure any AI key in the teammate's own `.env`. Develop on module branches and merge through PRs. GitHub publication and Moodle submission are separate actions.
