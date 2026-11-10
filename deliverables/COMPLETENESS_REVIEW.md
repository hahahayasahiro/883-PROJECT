# 项目与进度汇报完整性检查 / Project and progress completeness review

检查日期 / Review date: 10 November 2026.

结论：当前材料覆盖11月12日进度汇报需要的项目介绍、分工、当前进展、问题与下一步，系统具备三大子系统、六模块及跨模块流程。当前是进度原型交付，不能标记整个课程最终项目已经完成。

Conclusion: the current release covers the introduction, responsibilities, progress, problems and next steps for the 12 November progress presentation. It contains three subsystems, six modules and connected workflows. It is a progress prototype, not a completed final-course submission.

## 系统功能与证据 / Functions and evidence

| 检查内容 / Item | 当前状态 / Status | 证据与限制 / Evidence and limits |
| --- | --- | --- |
| 统一登录与权限 / Login and permissions | 已实现 / Implemented | 学生账号隔离、维护及审批权限由后端检查；本机演示认证，不代表生产部署完成。 |
| 学习助手 / Study assistant | 已实现 / Implemented | 保存会话、多轮追问、实际检索来源、模块入口；真实AI样例有既有证据，检索覆盖和答案准确率仍需评估。 |
| 学习路径 / Learning path | 已实现 / Implemented | 兴趣、目标、先修限制、学期计划及12学分演示上限；规则方案，无训练模型。 |
| 预约报障 / Facilities | 已实现 / Implemented | 筛选、冲突、替代场地、修改与取消、故障转维护；并发预约与修改已纳入测试。 |
| 维护能耗 / Maintenance | 已实现 / Implemented | 分类建议需人工确认；日志、费用、ETA和完成状态；能源为持久化模拟数据。 |
| 材料预审 / Pre-review | 已实现 / Implemented | TXT/文字PDF、字段候选确认、规则与AI证据、版本及过期结果；无OCR、无自动批准。 |
| 门户审批 / Portal | 已实现 / Implemented | 搜索、退回补件、修订重提、人工决定、时间线与站内通知；刷新加载，无邮件。 |
| 三条跨模块流程 / Connected flows | 已验证 / Recorded evidence | 学习会话到计划、预约报障到维护、预审到补件审批；既有浏览器记录无意外页面错误。 |
| 持久化与升级 / Persistence and upgrades | 已验证 / Tested | 重复迁移、旧库副本迁移、记录与账号保留；升级不重置。 |
| 自动化测试 / Automated tests | 34通过 / 34 passed locally | 本次重跑，本机原数据库副本可用；干净分发没有旧库副本时该专用用例会跳过。 |
| 依赖完整性 / Dependencies | 通过 / Passed | `pip check`无破损依赖；一个TestClient弃用警告仍存在，不影响本次结果。 |

Real AI connectivity was demonstrated earlier for conversation, pre-review, field extraction and classification; this audit does not relabel mock tests as new live-AI checks. Broader accuracy evaluation is pending. The local database and key are preserved privately.

真实AI连接证据来自此前独立调用，本次自动测试使用隔离数据、模拟与降级路径，不将其描述为新一轮真实AI验证。本机数据库和密钥继续保留在本地。

## 汇报材料 / Presentation package

| 内容 / Item | 检查结果 / Result |
| --- | --- |
| 英文PPT / English deck | 增强版13页，含封面；逐页复核既有渲染图；本次未修改幻灯片。 |
| 时间 / Timing | 六人各两页，50+70秒，共720秒；实际口述仍需计时排练。 |
| 分工 / Ownership | 六人各模块明确；怀喆元为System Analyst and Document Pre-review Lead，负责10—11页；集成和共享AI归属保持原分工。 |
| 课程要求 / Course presentation requirements | 介绍分工、进展、问题及下一步均有覆盖；操作须包含在各人2分钟内。 |
| 讲稿与演示 / Notes and demo | 增强版英文讲稿、操作指南、真实截图、无旁白备用录像齐备；截图细节较小，现场重点口述结果，必要时在本人时限内打开系统。 |
| 使用说明书 / User manual | 22页、20章，中英文逐段对照，可编辑Word。 |
| 提案 / Proposals | 原英文与最终中文版Word，以及中英文两页PDF副本已纳入docs/proposals；未改动原稿，不视为增强版需求已同步回旧提案。 |
| 提交时间 / Submission | 2026年11月12日课堂汇报；组长11月13日23:59前提交Moodle。GitHub发布不替代作业提交。 |

Current files are identified in [the delivery index](README.md). Older decks and reports are preserved as historical evidence and should not be presented as the current state. A matching package hash is checked against the saved validation receipt when reviewing the current PPTX locally.

## 本次整理及修复 / Corrections in this review

- 修正README末尾仍写“真实AI尚待验证”的旧表述，使其与已有独立AI证据一致。
- 补充当前交付索引、协作与上传指南、PR模板、Windows自动检查；原提案复制进入仓库，原文件保留。
- 收紧忽略规则，排除整个data目录、环境变体、私钥、备份及临时文件；加入换行与二进制文件约定。
- 安装脚本在数据库初始化失败时明确报错，避免仍显示“Ready”。
- 修正K15种子知识对数据发送范围的旧描述，涵盖新增字段提取与故障分类；仅更新匹配旧种子原文的记录，保留自定义政策及所有业务记录。

The changes correct documentation, repository packaging and setup failure reporting. The K15 seed-policy correction preserves customised knowledge and does not require resetting data or adding a new schema version. The presentation design and business workflow remain unchanged.

## 必须继续完成 / Pending work

1. 第二台实体电脑全新安装、账号登录、基础流程及本机AI配置验证。当前电脑中的干净副本安装只能验证分发文件完整，不能替代第二台硬件验证。
2. 六人完整计时排练，检查交接与投影可读性；在实际PowerPoint及教室设备上试播，备好增强版录像。
3. 首次GitHub推送后检查远程文件及Actions结果，再由组长按时提交Moodle。准备阶段不能声称远程已经更新或云端CI已通过。
4. 最终项目汇报PPT、最终项目报告及最终交付包仍属后续工作；课程简版说明给出的最终提交截止为2026年12月13日23:59，应持续核对课程最新公告。
5. 建立更丰富的问答与材料准确率评估；OCR、语音、训练风险模型、真实设备、预测维护、邮件及人员工作量分派仍在后续范围。

## GitHub准备状态 / Repository preparation

目标仓库为公开的hahahayasahiro/883-PROJECT，检查时为空且当前连接账号有写权限。已在应用目录建立本地Git仓库并设置origin；后续以Git状态与提交记录为准。准备期间没有执行push，也未创建线上PR、分支或Release。

The target repository was empty and accessible with write permission when checked. The local repository uses this application directory as its root and points origin to the target. No remote push, PR, branch or Release is implied by preparation. The repository audit checks candidate-file paths, size, private-key byte patterns and Office archive contents; it does not perform OCR or transcribe recordings. Current screenshots and recorded flows use synthetic data and avoid private configuration screens.
