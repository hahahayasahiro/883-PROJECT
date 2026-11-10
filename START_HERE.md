# 小组开始使用

系统已经有六个模块和三条贯通流程。现有提案保留在上一级目录，这个文件夹是应用项目。

## 现在打开

如果服务正在运行，访问 http://127.0.0.1:8000 。否则双击 `start.cmd`。

首次在另一台电脑上使用：安装 Python 3.12，进入此目录，在 PowerShell 运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

然后双击 `start.cmd`，在浏览器打开上面的地址。第一次安装依赖需要网络。

账号为 `student`、`student2`、`admin`、`maintenance`，密码均为 `Campus2026!`。学生流程使用 student，审批使用 admin，维修处理使用 maintenance。

## 开启真实 AI

本机 `.env` 已配置并验证 DeepSeek，密钥不会进入交付包。换电脑时需要自行配置，保存后重启服务。不要把密钥发在群聊、截图或提交到 GitHub。每次操作的 `live_ai` 才表示本次真实调用成功；AI可能失败或返回不合格结果，仍保留规则检查及手动操作。

## 六个人怎么接手

每个人的页面在 `static/modules`，对应后端在 `app/routers`。文件名分别为 assistant、learning、facilities、maintenance、reviews、applications。具体分工、公共文件归属、GitHub 分支约定都在 README.md。先完整跑一遍演示，再开始各自改动。公共数据库结构和页面样式由指定负责人维护。

## 两天后汇报

增强版资料为 `deliverables/SmartCampus-enhanced-presentation.pptx`、`SPEAKER_NOTES_ENHANCED.md`、`ENHANCED_GUIDE.md` 和 `ENHANCED_TEST_REPORT.md`。13页，每人2分钟；怀喆元负责第10—11页。新增录像 `SmartCampus-enhanced-demo.webm` 展示增强流程。早期PPT和离线录像保留作历史版本。

升级时重新运行 setup.ps1 安装新增依赖，然后启动系统。数据库会增量升级，不要重置已有记录。仍需你们在第二台电脑安装，并在PowerPoint和教室设备上排练。GitHub目标仓库为 hahahayasahiro/883-PROJECT，上传准备见 GITHUB_UPLOAD.md；本地配置远程地址不代表已经发布。

完整中英文使用说明书、当前汇报文件和历史资料的区分见 deliverables/README.md。项目与汇报完整性检查见 deliverables/COMPLETENESS_REVIEW.md。当前版本用于进度汇报，最终项目报告与最终汇报PPT仍为后续交付。

如果要重新演示初始状态，先停止服务，然后运行 `.\.venv\Scripts\python.exe manage.py --reset --yes`。该操作会删除本机演示过程中创建的记录，恢复虚构种子数据。
