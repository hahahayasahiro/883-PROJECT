"""Author the bilingual manual using the supplied document runtime."""
from pathlib import Path
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables'/'SmartCampus_中英文对照使用说明书.docx'
doc=Document()
s=doc.sections[0];s.page_width=Cm(21);s.page_height=Cm(29.7)
s.top_margin=Cm(1.8);s.bottom_margin=Cm(1.7);s.left_margin=Cm(2);s.right_margin=Cm(2)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3']:
 st=doc.styles[name];st.font.name='Arial';st.font.color.rgb=RGBColor(0,0,0)
 st.element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Microsoft YaHei')
st=doc.styles['Normal'];st.font.size=Pt(10.5)
st.paragraph_format.space_after=Pt(4);st.paragraph_format.line_spacing=1.12
doc.styles['Title'].font.size=Pt(27)
doc.styles['Subtitle'].font.size=Pt(15)
doc.styles['Heading 1'].font.size=Pt(17)
doc.styles['Heading 1'].paragraph_format.space_after=Pt(12)
doc.styles['Heading 2'].font.size=Pt(12)
doc.styles['Heading 2'].paragraph_format.space_before=Pt(9)
doc.styles['Heading 2'].paragraph_format.space_after=Pt(5)
footer=s.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=footer.add_run('SmartCampus  使用说明  User manual     ');r.font.size=Pt(8)
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
doc.core_properties.title='SmartCampus 中英文对照使用说明书'
doc.core_properties.subject='Enhanced prototype user manual in Chinese and English'
doc.core_properties.author='SmartCampus Project Team'

def p(text,bold=False,style=None):
 x=doc.add_paragraph(style=style);r=x.add_run(text);r.bold=bold;return x
def pair(cn,en):
 a=p(cn);a.paragraph_format.keep_with_next=True
 b=p(en);b.paragraph_format.space_after=Pt(8)
 return a,b
def sub(cn,en):doc.add_heading(cn+'  '+en,level=2)
def step(n,cn,en):pair(str(n)+'  '+cn,str(n)+'  '+en)
def code(text):
 x=p(text);x.paragraph_format.left_indent=Cm(.3);x.paragraph_format.space_before=Pt(4);x.paragraph_format.space_after=Pt(8)
 for r in x.runs:r.font.name='Consolas';r.font.size=Pt(9)
def table(headers,data,widths):
 t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 for c,w in zip(t.columns,widths):c.width=Cm(w)
 for i,row in enumerate([headers]+data):
  cells=t.rows[0].cells if i==0 else t.add_row().cells
  for j,(cell,text) in enumerate(zip(cells,row)):
   cell.width=Cm(widths[j]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   cell.text=text
   tcpr=cell._tc.get_or_add_tcPr();margins=OxmlElement('w:tcMar')
   for edge in ['top','bottom','left','right']:
    el=OxmlElement('w:'+edge);el.set(qn('w:w'),'90');el.set(qn('w:type'),'dxa');margins.append(el)
   tcpr.append(margins)
   borders=OxmlElement('w:tcBorders')
   for edge in ['top','left','bottom','right']:
    el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
   tcpr.append(borders)
   if i==0:
    sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'DCE6F1');tcpr.append(sh)
   for par in cell.paragraphs:
    par.paragraph_format.space_after=Pt(3);par.paragraph_format.line_spacing=1.05
    for run in par.runs:run.font.size=Pt(9);run.bold=i==0
  pr=t.rows[i]._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
 t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
 p('')
 return t

chapters=[
 ('系统概览','System overview'),('安装与启动','Installation and startup'),('AI配置与数据处理','AI configuration and data handling'),('登录与角色权限','Sign in and role permissions'),('学习助手','Study assistant'),('学习路径与学期计划','Learning path and semester plans'),('场地搜索与预约','Room search and reservations'),('预约管理与故障上报','Booking management and fault reports'),('维修处理与工作记录','Maintenance and work history'),('能耗与费用统计','Energy and cost statistics'),('申请准备与材料上传','Application preparation and uploads'),('字段提取与智能预审','Field extraction and pre review'),('版本比较与申请提交','Version comparison and submission'),('服务门户与工作人员审批','Service portal and staff decisions'),('补件重提与站内通知','Corrections and notifications'),('完整操作示例','Complete workflow examples'),('常见问题与处理','Troubleshooting'),('备份升级与重置','Backup upgrade and reset'),('小组交接与演示准备','Team handover and demonstration'),('状态与限制速查','Status and limits reference')]

p('SmartCampus',style='Title')
p('中英文对照使用说明书',style='Title')
p('Chinese and English User Manual',style='Subtitle')
pair('适用版本为六模块增强版。面向学生、行政工作人员、维护人员及小组安装维护人员，按实际界面说明日常操作、限制与异常处理。','This manual covers the enhanced six-module release for students, administrative staff, maintenance staff and the team members who install and maintain it. It explains actual controls, operating limits and recovery steps.')
pair('系统访问地址为 http://127.0.0.1:8000。所有用户、课程、政策和业务记录均为虚构演示数据；本系统不是学校正式办事平台。','Open http://127.0.0.1:8000. All users, courses, policies and business records are fictional demonstration data. This is not an official university service.')
pair('版本日期为2026年11月10日。每个中文步骤后紧跟对应英文；按钮保留界面原文。界面默认使用英文，本文提供中文对照。','Version date: 10 November 2026. Each Chinese instruction is followed by its English equivalent. Button labels match the English interface; the application does not provide a Chinese language switch.')
sub('快速开始','Quick start')
step(1,'首次使用先运行 setup.ps1，安装后双击 start.cmd；本机服务已运行时可直接打开网址。','For first use, run setup.ps1 and then double-click start.cmd. If the local server is already running, open the URL directly.')
step(2,'使用 student 登录学生功能，使用 admin 审批，使用 maintenance 处理维修；演示密码均为 Campus2026!。','Use student for student features, admin for decisions and maintenance for repairs. All demonstration passwords are Campus2026!.')
step(3,'AI操作后查看本次结果模式。live_ai 表示调用获得可用结果，不代表内容一定正确。','Check the result mode after each AI operation. live_ai indicates a usable live result, not guaranteed correctness.')

doc.add_page_break();doc.add_heading('目录 Contents',level=1)
pair('按任务查阅对应章节。目录标题可点击跳转；页码由Word在排版时更新。','Use the chapter for your task. Contents entries link to the corresponding headings; Word updates page numbers during layout.')
for i,(cn,en) in enumerate(chapters,1):
 par=doc.add_paragraph();par.paragraph_format.space_after=Pt(5)
 link=OxmlElement('w:hyperlink');link.set(qn('w:anchor'),'chapter'+str(i))
 run=OxmlElement('w:r');txt=OxmlElement('w:t');txt.text=f'{i}  {cn}  {en}';run.append(txt);link.append(run);par._p.append(link)
 par.add_run('    ');fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),f'PAGEREF chapter{i} \\h');par._p.append(fld)

def chapter(n):
 doc.add_page_break();cn,en=chapters[n-1];h=doc.add_heading(f'{n}  {cn}  {en}',level=1)
 b=OxmlElement('w:bookmarkStart');b.set(qn('w:id'),str(n));b.set(qn('w:name'),'chapter'+str(n));h._p.insert(0,b)
 e=OxmlElement('w:bookmarkEnd');e.set(qn('w:id'),str(n));h._p.append(e)

chapter(1)
pair('SmartCampus把学习支持、设施资源与行政服务放在同一入口。左侧导航打开六个模块，顶部显示当前用户与角色，Sign out 用于退出。','SmartCampus connects learning support, facilities and administrative services. The left navigation opens six modules, the header identifies the signed-in user and role, and Sign out ends the session.')
table(['界面入口 / Navigation','主要用途 / Main task'],[
 ['Study assistant','校园问答与历史会话 / Campus questions and saved conversations'],['Learning path','兴趣建议与学期计划 / Interest-based suggestions and semester plans'],['Spaces & bookings','筛选场地、预约与报障 / Search rooms, manage bookings and report faults'],['Energy & maintenance','维修记录与模拟能耗 / Repair histories and synthetic energy readings'],['Document pre-review','材料、字段、预审与版本 / Materials, fields, checks and versions'],['Service portal','申请、补件、审批与通知 / Applications, corrections, decisions and notifications']],[5.2,11.8])
pair('建议先以 student 完成学习与预约，再测试材料申请；需要工作人员动作时退出后换用对应账号。看到无权限提示时，先核对右上角角色。','Start as student for learning, bookings and applications. Sign out and use the appropriate staff account for restricted actions. If access is denied, check the role in the header first.')
pair('数据保存在本机数据库。刷新通常不会删除已保存记录，但尚未保存的表单可能丢失。换电脑或换浏览器不会自动复制本机数据库与会话选择。','Saved records live in the local database. Refresh normally preserves saved data but can discard unsaved form edits. Another computer or browser does not automatically receive the database or your current selections.')

chapter(2)
step(1,'将交付包解压到可写目录，进入包含 setup.ps1 与 start.cmd 的 smartcampus 文件夹。不要直接在压缩包内运行。','Extract the delivery archive into a writable folder and open smartcampus, which contains setup.ps1 and start.cmd. Do not run it inside the ZIP viewer.')
step(2,'安装Python 3.12，并确认PowerShell执行 python --version 能显示版本。浏览器使用Chrome或Edge；下载依赖及调用AI需要网络。','Install Python 3.12 and verify python --version in PowerShell. Use Chrome or Edge. Internet is required for dependency installation and live AI calls.')
code('python --version\npowershell -ExecutionPolicy Bypass -File .\\setup.ps1')
step(3,'setup.ps1 创建 .venv、安装锁定依赖、在必要时创建 .env，并初始化或增量升级数据库。已有配置与记录会保留。','setup.ps1 creates .venv, installs locked dependencies, creates .env only if missing, and initializes or incrementally upgrades the database. Existing configuration and records are preserved.')
step(4,'双击 start.cmd 或在当前目录运行 .\start.cmd。保持服务窗口开启，然后访问 http://127.0.0.1:8000。','Double-click start.cmd or run .\\start.cmd in this directory. Leave the server window open and visit http://127.0.0.1:8000.')
step(5,'停止服务时在其窗口按 Ctrl+C。正常再次启动只需运行 start.cmd；更新了依赖时重新运行 setup.ps1。','Press Ctrl+C in the server window to stop it. For normal subsequent starts, run start.cmd. Rerun setup.ps1 after dependency updates.')
pair('地址127.0.0.1只指当前电脑。手机或同学电脑不能通过其自己的127.0.0.1访问这台电脑；本版默认未开放局域网或公网服务。','127.0.0.1 refers to the device on which it is opened. A phone or teammate cannot reach this machine using their own loopback address. This release is not exposed to the LAN or public internet by default.')

chapter(3)
step(1,'本机已配置并验证DeepSeek。交付包不含密钥；换电脑后在项目根目录的 .env 配置自己的密钥，不要修改 .env.example 来保存真实密钥。','DeepSeek is configured and verified on the current machine. Archives exclude the key. On another computer, enter your own key in the project-root .env, not in .env.example.')
code('DEEPSEEK_API_KEY=<your local key>\nDEEPSEEK_BASE_URL=https://api.deepseek.com\nDEEPSEEK_MODEL=deepseek-flash')
step(2,'保存后重启服务。打开Study assistant询问CS202的先修课，检查结果为live_ai并附有来源；再在预审中检查逐项结果。','Save and restart the server. Ask about CS202 prerequisites in Study assistant and check for live_ai plus source references. Then check itemized results in pre-review.')
pair('每次AI请求最多等待约30秒。网络、余额、权限、模型名、结果格式或证据校验问题都可能导致降级；以前调用成功不保证以后每次成功。','An AI request waits approximately 30 seconds at most. Network, balance, permissions, model selection, output format or evidence validation can trigger fallback. Earlier success does not ensure every future request succeeds.')
pair('上传材料的本地文字提取不会自动调用AI。点击字段提取、智能预审或故障分类按钮，才发送该操作所需的材料或描述。学习问答会发送问题、检索来源和最近最多10轮所选会话内容。','Local upload text extraction does not call AI. Field extraction, pre-review and fault classification send their relevant input only when requested. Questions send the question, retrieved sources and at most ten previous turns from the selected conversation.')
pair('只使用虚构演示数据。不要上传真实身份证件或敏感学籍资料，不要把密钥放入截图、PPT、源代码或群聊。AI结果须人工核对，不能代替正式学校政策或工作人员决定。','Use fictional data only. Do not upload real identity documents or sensitive student records, or include keys in screenshots, slides, source code or chats. Check AI output manually; it does not replace official policy or staff decisions.')

chapter(4)
table(['用户名 / Username','身份 / Identity','密码 / Password'],[
 ['student','Alex Morgan / S1001 / 学生 Student','Campus2026!'],['student2','Jamie Chen / S1002 / 学生 Student','Campus2026!'],['admin','行政工作人员 / Administrative staff','Campus2026!'],['maintenance','维护工作人员 / Maintenance staff','Campus2026!']],[3.2,9,4.8])
step(1,'在登录页输入用户名和密码，点击 Sign in。右上角出现姓名和角色后再操作。','Enter the username and password and select Sign in. Confirm the name and role in the header before proceeding.')
step(2,'切换身份时先点击 Sign out，再使用另一个账号登录；不要把用户名输入到其他业务表单来尝试切换身份。','Select Sign out before signing in as another account. Entering a different name in a business form does not change your account.')
pair('学生只能读取自己的会话、计划、申请、版本、通知和报障记录。行政人员可以查看申请队列及其预审和时间线，作出退回、批准或拒绝决定。只有maintenance可以更新维修状态和处理费用。','Students can access only their own conversations, plans, applications, versions, notifications and fault reports. Admin can inspect the application queue, reviews and timeline, then return, approve or reject submissions. Only maintenance can update repair status and costs.')
pair('会话、偏好和业务记录保存在服务器数据库；部分选择或筛选条件仅保存在当前浏览器。登录会话最长8小时，过期后重新登录即可。','Conversations, preferences and business records are stored server-side. Some selections and filters are browser-local. Login sessions last at most eight hours; sign in again after expiration.')
pair('本版没有自助注册、忘记密码或修改账户资料功能。表单中的姓名、学号、邮箱必须与登录学生一致；student的邮箱是student@gcu.example，student2的邮箱是student2@gcu.example。','This release has no registration, password recovery or profile-editing feature. Application name, student ID and email must match the signed-in student. The addresses are student@gcu.example and student2@gcu.example respectively.')

chapter(5)
step(1,'打开Study assistant。点击New conversation新建对话；下拉框可切换以前保存的会话。','Open Study assistant. Select New conversation to start a new thread, or use the dropdown to reopen saved conversations.')
step(2,'在Your question输入问题，点击Ask assistant；也可点击Quick questions中的题目将其填入输入框，再提交。','Enter a question in Your question and select Ask assistant. Quick questions populate the input; select Ask assistant to send it.')
step(3,'示例先问“What are the prerequisites for CS202?”，再问“What does it require?”。系统重新检索来源，并将所选会话最近最多10轮作为上下文。','First ask “What are the prerequisites for CS202?”, then “What does it require?”. The system retrieves evidence again and uses up to ten previous turns of the selected conversation as context.')
step(4,'在Conversation & sources查看本次模式和回答；点击带[K02]等编号的来源标题，展开原文并核对。来源编号不等于对回答每一句都作出正确性保证。','Read the mode and answer in Conversation & sources. Expand a source such as [K02] to inspect its text. A citation is not proof that every generated statement is correct.')
step(5,'预约或成绩单问题可能显示Find a space或Prepare an application链接。点击只会进入相应模块，不会自动预约或提交申请。','Room or transcript questions may offer Find a space or Prepare an application. These links navigate to a module and do not book or submit anything automatically.')
pair('已提交的问答会保存，刷新后可重新选择。没有来源时显示no_evidence；AI不可用时显示retrieval_only并保留片段。此版没有会话删除或自定义重命名按钮，标题通常取首个问题。','Submitted turns are saved and can be reopened after refresh. no_evidence indicates no matching source; retrieval_only preserves excerpts when AI is unavailable. This version has no conversation deletion or manual-renaming control; titles normally derive from the first question.')

chapter(6)
step(1,'以student打开Learning path。在Interest area选择computing、ai、mathematics或management，填写Learning goal，点击Save preferences。','As student, open Learning path. Choose computing, ai, mathematics or management in Interest area, enter a Learning goal, and select Save preferences.')
step(2,'查看Ranked course suggestions中的解释。兴趣与先修关系参与规则排序；ai方向会提高部分基础课程的顺序，学习目标文字会保存但不会自动生成课程。','Read the reasons in Ranked course suggestions. Interest and prerequisites affect rule-based ordering. AI interest promotes some foundations. Goal text is saved but does not itself generate courses.')
step(3,'在Semester填写学期名称，例如2027 Semester 1，点击Open plan打开该名称对应的计划。以后需使用同一名称再次打开；本版没有学期列表选择器。','Enter a term name such as 2027 Semester 1 and select Open plan. Reuse the exact name to reopen it later; there is no saved-term picker in this release.')
step(4,'对需要的课程点击Add to plan。已加入的课程显示在Semester plan，点击Remove可移除。检查顶部学分总数，记录会自动保存。','Select Add to plan for a course. It appears in Semester plan, where Remove deletes that entry. Check the credit total. Changes are saved immediately.')
pair('每门种子课程3学分，每学期上限12学分。重复课程、已通过课程或未满足先修条件的课程会被拒绝；在同一计划里加入先修课不等于已通过该先修课。','Seed courses carry three credits and each term allows twelve. Duplicate, already-passed or ineligible courses are rejected. Adding a prerequisite to the same plan does not count as having passed it.')
pair('成绩低于50或出勤低于75%会出现说明和行动建议。例如MA101提示联系导师、复习遗漏内容与安排学习时间。这些是虚构规则，不是机器学习预测或学校正式预警。','A mark below 50 or attendance below 75% triggers an explanation and action checklist, such as tutor support and study sessions for MA101. These are synthetic rules, not trained predictions or official warnings.')

chapter(7)
step(1,'打开Spaces & bookings，在Find an available space选择From与To、People人数、Type类型、Equipment设备。设备可选projector、computers、whiteboard或wifi。','Open Spaces & bookings. In Find an available space, set From, To, People, Type and Equipment. Equipment choices include projector, computers, whiteboard and wifi.')
step(2,'点击Search available rooms。结果是同时满足条件且在该时段无活动预约的场地；没有结果时降低人数、取消设备限制或更换时段。','Select Search available rooms. Results meet the filters and have no active overlap in that interval. If none match, reduce capacity, relax equipment or change the time.')
step(3,'点击某结果的Use this room，将场地与搜索时段带入Reserve a room。再次核对表单后点击Save booking。仅学生账号可预约。','Select Use this room to copy that room and the search interval into Reserve a room. Check the form, then select Save booking. Only student accounts can reserve.')
step(4,'预约必须在未来，结束晚于开始，时长不超过2小时。若提交时已被别人占用，会提示冲突并显示当前可用替代场地；替代列表不沿用全部搜索筛选，选择后需再核对容量与设备。','The interval must be in the future, end after start and last at most two hours. A conflict returns currently available alternatives. The alternative list does not preserve every search filter, so recheck capacity and equipment before choosing.')
pair('表单按设备本地时区输入，保存时转换为UTC。Daily timetable的日期筛选按UTC日计算，具体时间仍按浏览器本地时间显示；中国时间凌晨可能落在前一个UTC日期。','Forms use the device timezone and save UTC timestamps. Daily timetable filters by UTC date, while displayed timestamps use browser-local time. An early-morning time in China may belong to the previous UTC date.')
pair('搜索不是锁定场地。即使刚查到可用，正式提交时也会再次检查冲突。系统不提供候补排队、重复预约或付款功能。','Search results do not hold a room. Availability is checked again when saving. Waitlists, recurring reservations and payments are not provided.')

chapter(8)
sub('修改和取消','Modify and cancel')
step(1,'在Your booking history找到自己的active预约，点击Modify，将原数据带入表单；调整场地或时间后点击Save booking。修改冲突时原预约保持不变。','Find your active reservation in Your booking history and select Modify. Adjust the room or times and select Save booking. A conflicting update leaves the original reservation unchanged.')
step(2,'New reservation仅退出当前修改模式，不会删除已有预约。要取消，在记录中填写Cancellation reason后点击Cancel reservation。','New reservation exits edit mode without deleting the existing booking. To cancel, enter a Cancellation reason and select Cancel reservation on the record.')
pair('取消原因至少3个字符。取消后状态变为cancelled、释放时段并保留历史；不能用取消操作修改别人的记录。','A cancellation reason needs at least three characters. Cancellation changes the state to cancelled, releases the slot and preserves the history. You cannot cancel another student’s reservation.')
sub('故障上报','Report a fault')
step(3,'在Report a fault选择Room并输入Description。可点击Ask AI for category suggestion，查看原因，然后点击Apply suggestion to editable fields。','In Report a fault, choose Room and enter Description. Optionally select Ask AI for category suggestion, read the reason, and select Apply suggestion to editable fields.')
step(4,'核对Category和Priority，可手动修改。点击Confirm & send fault才正式生成工单，并跳转维修页面。应用AI建议本身不会提交。','Check Category and Priority and edit them if needed. Only Confirm & send fault creates the ticket and opens maintenance. Applying an AI suggestion alone does not submit.')
pair('分类包括electrical、hvac、it、plumbing、other，优先级为low、normal、high。AI失败时可直接手动选择；报障后保留工单编号，供后续跟踪。','Categories are electrical, hvac, it, plumbing and other; priorities are low, normal and high. Choose manually if AI fails. Keep the ticket number for follow-up.')

chapter(9)
step(1,'退出学生账号，以maintenance登录，打开Energy & maintenance。按Ticket status、Priority、Room筛选后点击Apply filters。','Sign out and log in as maintenance. Open Energy & maintenance, choose Ticket status, Priority and Room, and select Apply filters.')
step(2,'打开待处理记录，核对描述、类别和优先级。填写Estimated completion预计完成时间及Update note。State选择in_progress后点击Save ticket details。','Inspect the description, category and priority. Enter Estimated completion and an Update note. Change State to in_progress and select Save ticket details.')
step(3,'在Work log记录具体工作，Additional expense填写此次新增费用，点击Add log & expense。费用会加到当前总额，并写入日志。','Describe work in Work log, enter this new charge in Additional expense and select Add log & expense. The amount is added to the total and recorded in history.')
step(4,'完成后将State改为completed，确认总费用并保存。必须先open再in_progress，不能从open直接跳到completed。完成后的工单为只读，不能继续追加日志或重开。','Set State to completed after finishing and save the checked total. Tickets must move from open to in_progress before completed. Completed tickets are read-only and cannot be reopened or appended to.')
step(5,'点击Show work history，查看上报、状态更新、处理人、说明、时间及费用调整。旧版本导入的记录可能没有历史明细，不代表数据被清空。','Select Show work history for the report, status updates, actors, notes, timestamps and cost adjustments. Imported older tickets may have no historical detail; their records were not cleared.')
pair('学生只能查看自己的报障与历史，不能保存维修更新；admin可以查看维修信息，但也不能代替maintenance更新。预计完成时间是人工输入，不是自动预测，也不会自动提醒。','Students can view their own reports and history but cannot update repairs. Admin can inspect maintenance information but cannot perform maintenance writes. ETA is manually entered, not predicted, and does not trigger automatic reminders.')

chapter(10)
sub('模拟能耗','Synthetic energy')
step(1,'在Energy & maintenance选择Room和Energy date，点击Apply filters。全部场地时显示所选日期各场地的合计用电及平均占用率。','Choose Room and Energy date in Energy & maintenance and select Apply filters. All rooms displays summed electricity and average occupancy for that date.')
step(2,'Energy profile柱形展示kWh，下面的百分比表示模拟占用率。日期来自数据库已有的7个种子日期；不是实时传感器数据，也不会每日自动补充。','Energy profile bars show kWh and the percentage shows simulated occupancy. Available dates are seven seeded dates stored in the database, not live sensor data or an automatically rolling daily feed.')
pair('同一场地与日期反复刷新应保持读数一致。没有读数时换到下拉框中已有日期；图表不能控制空调、灯光或设备开关。','Repeated requests for the same room and date should show the same readings. Use a listed date if no reading is available. The chart cannot control air conditioning, lighting or equipment.')
sub('费用解释','Cost interpretation')
pair('Matching tickets和Recorded cost in selection依据当前工单筛选计算，不是能耗账单。Room同时影响工单和能耗，Ticket status与Priority只影响工单，Energy date只影响图表。','Matching tickets and Recorded cost in selection reflect filtered tickets, not an energy bill. Room affects both sections; Ticket status and Priority affect tickets only; Energy date affects the chart only.')
pair('Total recorded cost是工单当前累计总额，不是本次新增费用。例如总额已有35，再输入35仍为35；要新增35应使用Additional expense，结果为70。','Total recorded cost is the ticket’s current accumulated amount, not a new charge. If it is already 35, saving 35 leaves it at 35. Use Additional expense to add another 35, producing 70.')
pair('手动修改总额会产生差额调整记录。日志中的cost adjustment可能为负，代表下调，并非负数收费；新增费用和总额必须是非负有效数字。美元符号仅为演示标签。','Changing the total records the difference as an adjustment. A negative adjustment means a reduction, not a negative charge. Added expenses and totals must be nonnegative finite numbers. The dollar symbol is a demonstration label.')

chapter(11)
step(1,'以student打开Document pre-review。在Continue an editable application选择已有draft或returned记录；New application表示准备新申请，不会删除旧申请。','As student, open Document pre-review. Select an existing draft or returned record in Continue an editable application. New application starts a new form without deleting earlier applications.')
step(2,'选择Application type：transcript或certificate。查看Required fields与Material清单，准备对应说明材料；certificate还需填写certificate_type。','Choose transcript or certificate in Application type. Read Required fields and Material. Certificates also require certificate_type.')
step(3,'选择本机TXT或文字型PDF，点击Extract text locally。文字将带入Material text，并显示文件名、页数和字符数；仍需保存草稿才附到申请。','Choose a local TXT or text-based PDF and select Extract text locally. Extracted content fills Material text and shows filename, page count and character count. Save the draft to attach the text and metadata.')
step(4,'也可直接在Material text粘贴或修改内容。更换或粘贴材料后先核对表单，不要误以为文件名证明了原文件内容；系统长期保留的是提取文本和文件名等信息，不是原文件。','You may paste or edit Material text directly. Check the form after replacement. A filename does not prove original content: the system retains extracted text and metadata, not the original uploaded file.')
pair('文件上限5MB，PDF最多20页，提取文本最多60,000字符。TXT需UTF-8编码且不能含二进制空字符。加密PDF、扫描件、包含无可提取文字页面的混合PDF和损坏文件会被拒绝。','Limits are 5MB, twenty PDF pages and 60,000 extracted characters. TXT must be UTF-8 without binary null characters. Encrypted, scanned, mixed PDFs containing a page without extractable text, or corrupt files are rejected.')
pair('可用示例位于deliverables/sample-materials。conflicting-application.txt故意写S9999，corrected-application.txt写S1001；这两个文件仅适用于student的演示身份。','Examples are in deliverables/sample-materials. conflicting-application.txt intentionally uses S9999; corrected-application.txt uses S1001. They are prepared for the student demonstration identity.')

chapter(12)
step(1,'检查Material text后点击Ask AI to extract fields。此时文字会发送给DeepSeek；返回的字段候选显示value与Evidence，不会自动覆盖表单。','Check Material text and select Ask AI to extract fields. Text is sent to DeepSeek. Returned field candidates show a value and Evidence without automatically replacing form fields.')
step(2,'只勾选正确候选，点击Apply selected candidates，再逐一核对Student ID、Full name、Email、Purpose与Certificate type。材料中的错误学号也可能被正确“提取”，但不能作为正确身份使用。','Select only correct candidates and choose Apply selected candidates. Recheck Student ID, Full name, Email, Purpose and Certificate type. Extraction may accurately copy a wrong ID from the material; that does not make it the correct identity.')
step(3,'Save draft only只保存；Save & pre-review会先保存草稿，再执行规则与AI分析。看到Version and pre-review saved提示后，检查右侧Checks & suggestions。','Save draft only saves without AI review. Save & pre-review first saves, then runs rules and AI analysis. After Version and pre-review saved, inspect Checks & suggestions.')
step(4,'逐项查看label、status、source、Evidence与Suggestion。rules是确定性检查，ai是带可核对证据的模型结果；pass、warning、fail均是预审结果，不是审批状态。','Read each label, status, source, Evidence and Suggestion. rules identifies deterministic checks and ai identifies model findings with verifiable evidence. pass, warning and fail are pre-review results, not approval states.')
pair('规则检查必填项、登录身份与学号冲突。AI可提示文本矛盾，但可能漏检或误判；证据校验只检查片段是否来自输入，不证明分析逻辑一定正确。','Rules check required fields, signed-in identity and conflicting IDs. AI may flag textual inconsistencies but can miss or misinterpret them. Evidence validation checks that excerpts occur in the input, not that the reasoning is necessarily correct.')
pair('rules_only表示仅规则结果可用；manual表示需要手填或手动分类。先修正确定性错误，再根据实际情况参考AI建议。AI预审不能直接批准申请。','rules_only means only deterministic findings are usable; manual requests manual entry or classification. Correct definite field errors first, then assess AI advice. Pre-review never approves an application.')

chapter(13)
step(1,'在Versions & review history展开Version查看与前一版本的差异，包括字段、材料、申请类型或文件名。实际内容变更才新增版本；无变化保存通常不新增。','Expand Version in Versions & review history to compare fields, material, kind or filename with the previous snapshot. Actual changes create a new version; an unchanged save normally does not.')
step(2,'展开Review for vN查看该版本的预审。OUTDATED表示它不再属于当前版本，结果不会被自动迁移到新材料；修改后需重新预审。','Expand Review for vN for that version’s findings. OUTDATED means it is not for the current version. Findings are not automatically applied to new content; request another review after edits.')
step(3,'同一版本可多次预审并保留记录。旧版升级前已删除的历史无法恢复。返回补件后重新保存时，即使文字未变，也会创建修订版本并回到draft。','Repeated reviews of one version remain recorded. History already deleted by earlier releases cannot be restored. Saving a returned application creates a revision and returns it to draft even if its text is unchanged.')
step(4,'点击Open service portal，在对应草稿点击Submit to staff。提交会再次检查必填项和登录身份；失败时回到Edit & pre-review修正并保存后重试。','Select Open service portal, then Submit to staff on the draft. Submission checks required fields and account identity again. On failure, use Edit & pre-review to correct, save and retry.')
pair('当前实现不强制要求存在AI成功结果，也不把所有材料矛盾设为提交硬拦截。能提交不表示材料没有问题，最终仍由admin审批；界面不会生成正式成绩单文件。','The implementation does not require a successful AI review or block every material contradiction at submission. Submission does not certify correctness; admin decides. The interface does not issue an official transcript file.')
pair('submitted记录不能由学生直接编辑。approved和rejected为终态；本版没有撤回、删除或对终态直接重开的按钮。需要新申请时使用New application。','Students cannot directly edit submitted records. approved and rejected are final in this release. There is no withdrawal, deletion or reopen control for final records. Use New application when another request is needed.')

chapter(14)
step(1,'打开Service portal，在Search ID, applicant or field输入关键词，可结合State与Type，点击Filter applications。清空筛选并再次点击可查看全部有权访问记录。','Open Service portal. Enter a term in Search ID, applicant or field, optionally choose State and Type, and select Filter applications. Clear filters and apply again for all accessible records.')
step(2,'展开Application fields and material查看字段与材料；点击Timeline & reviews查看办理事件和已保存预审。student只看到自己，admin看到申请队列。','Expand Application fields and material for the data, or choose Timeline & reviews for events and saved reviews. Students see their own records; admin sees the queue.')
step(3,'admin对submitted记录选择Decision：Return for corrections、Approve或Reject。填写至少3个有效字符的Explanation，点击Save staff decision。','For a submitted record, admin selects Return for corrections, Approve or Reject under Decision, enters an Explanation of at least three meaningful characters, and selects Save staff decision.')
step(4,'保存后状态、时间线与学生通知一同更新。查看证据和材料后再决定；规则或AI标记pass并不会替工作人员作决定。','Saving updates the state, timeline and student notification together. Inspect evidence and material before deciding. A pass result from rules or AI does not make the decision for staff.')
pair('Awaiting staff decision是当前账号可见记录中的submitted数量；平均处理时长仅计算有有效时间戳的最近一轮提交到终审，单位h。无可计算样本显示短横线，不是0小时。','Awaiting staff decision counts accessible submitted records. Average processing time uses valid timestamps for the latest submission-to-final-decision cycle, in hours. A dash means no calculable sample, not zero hours.')
pair('顶部数量是当前账号范围内的汇总，不随关键词筛选全部重算。导入记录没有真实历史时间，不会编造时长。本版未按工作人员分派工作，也不统计个人绩效。','Header counts summarize the account’s accessible records and are not all recomputed for keyword filters. Imported records with unknown timing do not receive invented durations. Work assignment and individual staff performance reporting are not implemented.')

chapter(15)
step(1,'admin选择Return for corrections，在Explanation写清需要补充的内容，例如补充实习单位，保存后申请变为returned。','Admin chooses Return for corrections, explains the missing detail, such as the internship organisation, and saves. The application becomes returned.')
step(2,'以student登录Service portal，展开Notifications查看通知。点击Mark read只改变已读状态，不等于已经补件或批准。','As student, open Service portal and expand Notifications. Mark read changes only read status; it does not complete corrections or approve anything.')
step(3,'在对应记录点击Correct returned application，进入预审页修改材料或用途。先Save draft only或Save & pre-review，让它成为新的draft修订版。','Choose Correct returned application, edit the material or purpose in pre-review, and use Save draft only or Save & pre-review to create a revised draft.')
step(4,'回到门户点击Resubmit to staff。admin再次核对后批准或拒绝；学生刷新门户并点击Timeline & reviews，可见returned、revised、resubmitted与最终决定。','Return to the portal and select Resubmit to staff. Admin reviews again and approves or rejects. Refresh the student portal and open Timeline & reviews for returned, revised, resubmitted and final events.')
pair('不能直接提交仍为returned的记录，必须先保存修订。旧Staff explanation会保留，可能仍出现在已重提的记录旁；应结合当前状态与时间线理解，不代表又被退回。','A returned record must be saved as a draft revision before resubmission. The earlier Staff explanation remains and may still appear after resubmission. Interpret it alongside the current state and timeline; it is not a new return.')
pair('通知需要刷新门户或重新进入页面才加载，不是推送或邮件。页面最多显示最近100条通知，未读总数可能包括更早记录；没有批量已读或删除按钮。','Notifications load on portal refresh or re-entry, not by push or email. The page lists the latest 100 notifications; the unread total can include older records. There is no mark-all-read or delete control.')

chapter(16)
sub('学习流程','Learning workflow')
step(1,'student新建会话，询问CS202先修课并追问，展开[K02]核对；进入Learning path选择ai，保存目标，打开指定学期并加入CS102。','As student, start a conversation about CS202 prerequisites, ask a follow-up and inspect [K02]. Open Learning path, choose ai, save a goal, open a named term and add CS102.')
sub('设施流程','Facilities workflow')
step(2,'选择未来1小时，筛选projector与20人场地，保存预约，再重复提交以展示冲突。通过Modify改时段或选替代场地，必要时填写原因取消。','Search a future one-hour slot with projector and capacity 20, save a booking and repeat to show conflict handling. Modify the time or choose an alternative, then cancel with a reason if needed.')
step(3,'报告投影仪闪烁，申请AI建议并人工确认，提交后记下工单编号。切换maintenance，将同一工单设为in_progress，追加35的费用与日志，再completed。','Report a flickering projector, request and confirm an AI suggestion, then submit and keep the ticket ID. As maintenance, set that ticket to in_progress, add a log with expense 35, then complete it.')
sub('材料与审批流程','Materials and decisions workflow')
step(4,'student上传conflicting-application.txt。核对AI候选，不应用错误学号。保存预审后将材料S9999改为S1001，复审并比较版本，再提交。','As student, upload conflicting-application.txt. Inspect AI candidates without applying the wrong ID. Save and review, correct S9999 to S1001, review again, compare versions and submit.')
step(5,'admin退回并要求写明实习单位；student阅读通知，修订为Internship at Fictional Campus Lab并重提；admin批准；student查看最终时间线。','Admin returns it with a request for the internship organisation. The student reads the notice, revises the purpose to Internship at Fictional Campus Lab and resubmits. Admin approves; the student inspects the final timeline.')
pair('记录你本次生成的申请和工单编号，不要假设示例始终是#1。不要为重复演示而清空同学已经创建的记录。','Use the application and ticket IDs created in your run rather than assuming #1. Do not reset teammates’ existing records merely to repeat the demonstration.')

chapter(17)
sub('服务与登录','Server and sign in')
pair('页面打不开：先确认start.cmd窗口仍在运行，地址为http而非https。127.0.0.1是本机；换电脑须各自安装。端口占用时先确认是否已有本项目服务，不要随意终止其他程序。','If the page cannot open, confirm start.cmd is still running and use HTTP, not HTTPS. Loopback is local; another device needs its own installation. For a busy port, check for an existing project server before stopping anything.')
pair('登录失败或会话过期：核对用户名、密码和右上角角色；重新登录。权限拒绝不靠修改表单姓名解决。界面没更新时刷新浏览器，但先保存正在编辑的内容。','For login failure or expiry, check credentials and role, then sign in again. Changing a form name does not grant permissions. Refresh stale UI only after saving edits.')
sub('AI与文件','AI and files')
pair('AI unavailable、rules_only或manual：检查本机配置、网络、余额和模型，改完重启。也可能是结果格式或证据校验失败；先用手动字段与规则检查继续，不要不停重复点击。','For AI unavailable, rules_only or manual, check local configuration, network, balance and model, then restart after edits. Output-format or evidence checks may also fail. Continue with manual entry and rules rather than repeatedly clicking.')
pair('上传被拒绝：将TXT另存为UTF-8；PDF检查是否为扫描、加密、超20页、超5MB或含无文字页面。只有文字图片不能通过改扩展名变成可读PDF；本版不做OCR。','If upload fails, save TXT as UTF-8 and check PDF text, encryption and size/page limits. Renaming an image does not make it a text-based PDF. OCR is not included.')
sub('业务状态','Workflow state')
pair('预约冲突：改时段或场地，搜索可用不代表已锁定。计划添加失败：检查先修课、重复课程、已通过状态和12学分上限。','For a booking conflict, change room or time; search does not hold a slot. For a plan failure, check prerequisites, duplicates, already-passed status and the twelve-credit cap.')
pair('申请无法提交：先保存，再检查身份与必填项；returned须先修订回draft。预审报“Application changed”时重新读取草稿再复审，勿沿用旧结果。','If submission fails, save and check identity and required fields; returned records need a draft revision. For Application changed during review, reload the draft and review again rather than using stale findings.')

chapter(18)
sub('日常备份与升级','Routine backup and upgrade')
step(1,'停止服务后，将data/campus.sqlite复制到带日期的本机备份文件；如需恢复配置，单独保管.env。备份含业务内容和登录信息，不应公开分发。','Stop the server and copy data/campus.sqlite to a dated local backup. Keep .env separately if configuration recovery is needed. Backups contain business and login information and should not be publicly shared.')
step(2,'升级前先备份。替换或更新应用文件时保留data与.env，重新运行setup.ps1并启动；迁移按版本执行，可重复启动，不需要reset。','Back up before upgrading. Preserve data and .env when updating application files, rerun setup.ps1 and start the server. Versioned migration is repeatable and does not require reset.')
step(3,'恢复时先停服，备份当前数据库，再用与当前版本兼容的副本替换campus.sqlite。重新启动并检查账号、历史与计划；不要在服务运行时替换数据库。','To restore, stop the server, back up the current database, then replace campus.sqlite with a compatible backup. Restart and check accounts, histories and plans. Never replace a live database.')
sub('恢复种子演示数据','Restore seed demonstration data')
pair('下列命令会删除本机全部演示状态，包括会话、计划、预约、申请、版本、预审、通知、工单与登录会话。仅在明确要清空且已经备份时使用；此操作不可从界面撤销。','The following command deletes all local demo state, including conversations, plans, bookings, applications, versions, reviews, notices, tickets and sessions. Use only after a deliberate decision and backup. The interface cannot undo it.')
code('.\\.venv\\Scripts\\python.exe manage.py --reset --yes')
pair('Git与交付包排除.env、数据库、备份和.venv。新电脑的安装不是复制本机历史；默认会建立新种子数据。预升级备份仅存在当前机器，不随交付包发出。','Git and release archives exclude .env, databases, backups and .venv. A new installation creates seed data rather than copying this machine’s history. The local pre-upgrade backup is not distributed.')

chapter(19)
table(['成员 / Owner','主要职责 / Responsibility'],[
 ['程荣凯 / Rongkai Cheng','学习助手与共享AI / Assistant and shared AI'],['尚得群 / Dequn Shang','学习建议与计划 / Learning suggestions and plans'],['杨骏 / Jun Yang','预约报障与系统集成 / Facilities and integration'],['舒乐熙 / Lexi Shu','维护、能耗与测试 / Maintenance, energy and QA'],['怀喆元 / Zheyuan Huai','需求分析、范围管理与材料预审 / Requirements, scope and pre-review'],['袁诗然 / Shiran Yuan','门户、通知与公共界面 / Portal, notices and shared UI']],[5.7,11.3])
pair('后端模块在app/routers，前端模块在static/modules。公共数据库与入口由集成负责人协调，公共界面由界面负责人协调；修改后先运行测试再合并。','Backend modules are in app/routers and browser modules in static/modules. Coordinate shared schema/entrypoint changes with integration and shared UI changes with the UI lead. Run tests before merging.')
code('.\\.venv\\Scripts\\python.exe -m pytest -q')
pair('可运行源码与配置示例可提交到小组仓库，但真实.env不能提交。本版尚未自动创建或推送GitHub仓库；六人分支和合并由小组实际执行。','Share source and example configuration through the team repository, never the private .env. The release does not automatically create or push a GitHub repository; the team manages branches and merges.')
pair('汇报使用SmartCampus-enhanced-presentation.pptx、SPEAKER_NOTES_ENHANCED.md与ENHANCED_GUIDE.md。13页，六人各2分钟，无独立加时演示；怀喆元负责第10—11页。','Use SmartCampus-enhanced-presentation.pptx, SPEAKER_NOTES_ENHANCED.md and ENHANCED_GUIDE.md. There are thirteen slides, two minutes per speaker and no separate demo slot. Zheyuan presents slides ten and eleven.')
pair('课堂汇报为2026年11月12日，组长于11月13日23:59前提交。提前在第二台电脑与课堂设备试运行并计时排练；本机测试与录像不能替代这些检查。','Present on 12 November 2026; the group leader submits by 23:59 on 13 November. Test another computer and the classroom equipment and rehearse timing. Local tests and a recording do not replace these checks.')

chapter(20)
table(['状态 / Status','含义 / Meaning'],[
 ['live_ai','本次有可用真实AI结果，仍需核对 / Usable live result; still verify it'],['retrieval_only','只有检索片段 / Retrieved excerpts only'],['no_evidence','没有匹配来源 / No matching source'],['rules_only / manual','只用规则或手动填写 / Rules only or manual input'],['draft / submitted','可编辑草稿 / 等待工作人员决定 / Editable draft / awaiting decision'],['returned','退回补件，需保存修订后重提 / Returned; save a revision before resubmitting'],['approved / rejected','批准或拒绝的终态 / Final approval or rejection'],['open / in_progress / completed','维修待处理、处理中、已完成 / Repair open, active, completed'],['pass / warning / fail','逐项预审结果，不是审批 / Review finding, not approval'],['OUTDATED','预审属于旧版本 / Review belongs to an older version']],[5,12])
pair('操作限额：预约未来时段且不超过2小时；学期计划最多12学分；文件最多5MB、PDF20页、提取文本60,000字符；会话最多10轮历史发送给AI；登录最长8小时。','Operating limits: future bookings up to two hours, twelve credits per term, uploads up to 5MB/twenty PDF pages/60,000 extracted characters, at most ten previous conversation turns sent to AI, and eight-hour login sessions.')
pair('当前未提供：自助注册、账号资料修改、会话删除、实时邮件、OCR、真实设备控制、训练预测模型、个人工作人员工作量分配及正式证书文件生成。需要这些能力时先纳入后续需求，不要在汇报中说成已完成。','Not provided: self-registration, profile editing, conversation deletion, email delivery, OCR, physical control, trained predictions, individual staff workload assignment or official certificate-file issuance. Treat these as future requirements, not completed features.')

OUT.parent.mkdir(parents=True,exist_ok=True)
for border in list(doc.styles.element.iter(qn('w:pBdr'))):
    border.getparent().remove(border)
for border in list(doc.element.iter(qn('w:pBdr'))):
    border.getparent().remove(border)
doc.save(OUT)
print(OUT)
