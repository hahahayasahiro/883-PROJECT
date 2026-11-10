import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const workspaceDir=path.resolve(import.meta.dirname,'..');
const dep=process.env.CAMPUS_RUNTIME_MODULES;
if(!dep)throw Error('Set CAMPUS_RUNTIME_MODULES to the supplied runtime package directory.');
process.env.RUNTIME_NODE_MODULES=dep;
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(dep,'@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const SKILL_DIR=process.env.CAMPUS_SLIDE_SKILL;
const RUNTIME_PYTHON=process.env.CAMPUS_RUNTIME_PYTHON;
const out=path.join(workspaceDir,'deliverables');
const build=path.join(workspaceDir,'.build');await fs.mkdir(build,{recursive:true});await fs.mkdir(out,{recursive:true});
const presentation=Presentation.create({slideSize:{width:1280,height:720}});
const notes=await fs.readFile(path.join(out,'SPEAKER_NOTES.md'),'utf8');
const noteSections=notes.split(/^## /m).slice(1);
const font='Arial';
function text(slide,value,x,y,w,h,size=26,color='#163d36',bold=false){const s=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});s.text=value;s.text.style={fontFamily:font,fontSize:size,color,bold};return s;}
function slide(title,index){const s=presentation.slides.add();s.background.fill='#f5f7f4';text(s,title,64,52,1152,95,42,'#163d36',true);text(s,`SmartCampus prototype     ${String(index).padStart(2,'0')}`,64,670,1152,24,14,'#6b8177');s.speakerNotes.text=noteSections[index-1]||'';return s;}
async function screenshot(s,file){const bytes=await fs.readFile(path.join(out,'screenshots',file));s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt:file.replace('.png',''),fit:'contain',position:{left:555,top:180,width:665,height:440}});}
let s=slide('SmartCampus',1);s.background.fill='#143e37';s.shapes.items[0].text.style={fontFamily:font,fontSize:76,bold:true,color:'#ffffff'};text(s,'Working prototype',66,210,1030,95,48,'#d4ebc5');text(s,'Learning support, campus facilities and administrative services',66,350,1000,110,31,'#c8ddd5');text(s,'CSIT883 progress presentation\n12 November 2026',66,520,1000,80,23,'#c8ddd5');s.shapes.items[1].text.style={fontFamily:font,fontSize:14,color:'#c8ddd5'};
s=slide('Architecture and prototype scope',2);text(s,'Browser',64,190,500,55,34,'#136c60',true);text(s,'Six local HTML and JavaScript pages',64,250,1090,45,28);text(s,'FastAPI server',64,335,500,55,34,'#136c60',true);text(s,'Shared authentication, six routers and one AI adapter',64,395,1090,45,28);text(s,'SQLite and DeepSeek',64,480,600,55,34,'#136c60',true);text(s,'Persistent synthetic records and two AI-assisted workflows',64,540,1090,65,28);s.speakerNotes.text+='\nTechnical reference: https://api-docs.deepseek.com/ . AI service access remains to be verified with a team key.';
const modules=[
 ['Study assistant','Rongkai Cheng','Local retrieval over 15 fictional documents.','Answers cite retrieved source IDs.','Unavailable API shows source excerpts.','03-assistant.png'],
 ['Learning path','Dequn Shang','Course suggestions check prerequisites.','Low marks or attendance trigger reminders.','Rules remain visible and explainable.','04-learning.png'],
 ['Spaces and bookings','Jun Yang','Bookings persist and reject overlaps.','Students cancel their own reservations.','Fault reports become shared repair tickets.','05-booking-conflict.png'],
 ['Energy and maintenance','Lexi Shu','Staff advance repair tickets to completion.','Each completed repair records a cost.','Energy readings are explicitly simulated.','10-maintenance.png'],
 ['Document pre-review','Zheyuan Huai','Field rules catch missing or mismatched data.','DeepSeek reviews supporting text.','Students correct and recheck saved drafts.','07-review-issue.png'],
 ['Service portal','Shiran Yuan','Students submit and track applications.','Only administrative staff decide outcomes.','Decision notes return to the student view.','12-student-approved.png'],
];
for(let i=0;i<modules.length;i++){const [title,owner,a,b,c,image]=modules[i];s=slide(title,i+3);text(s,owner,64,165,460,45,23,'#6b8177');text(s,a,64,255,455,100,29,'#163d36',true);text(s,b,64,380,455,85,26);text(s,c,64,490,455,85,26);await screenshot(s,image);}
s=slide('Three connected workflows',9);text(s,'01   Learning support',64,185,1110,50,34,'#136c60',true);text(s,'A course question, supporting sources and a learning suggestion',64,245,1110,70,27);text(s,'02   Campus facilities',64,335,1110,50,34,'#136c60',true);text(s,'A reservation, conflict rejection and a completed repair',64,395,1110,70,27);text(s,'03   Administrative services',64,485,1110,50,34,'#136c60',true);text(s,'A corrected draft, staff approval and a student status update',64,545,1110,70,27);
s=slide('Verification and next steps',10);text(s,'Verified locally',64,190,520,55,33,'#136c60',true);text(s,'12 backend test cases\nConnected browser workflows\nOwnership and conflict rejection\nAI adapter failures and fallback modes',64,265,550,220,27);text(s,'Team follow-up',695,190,520,55,33,'#136c60',true);text(s,'Verify both live AI features with a key\nInstall on a second computer\nEvaluate answers and review quality\nExtend features after the demo freeze',695,265,510,240,27);text(s,'Synthetic data, explicit rules and advisory AI define this prototype release.',64,570,1150,60,24,'#6b8177');
for(let i=0;i<presentation.slides.items.length;i++){const img=await presentation.export({slide:presentation.slides.items[i],format:'png',scale:1});await fs.writeFile(path.join(build,`slide-${i+1}.png`),new Uint8Array(await img.arrayBuffer()));}
const draft=path.join(build,'candidate.pptx');await (await PresentationFile.exportPptx(presentation)).save(draft);
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL_DIR,'container_tools/artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({workspaceDir,candidatePath:draft,finalPath:path.join(out,'SmartCampus-progress.pptx'),pythonExecutable:RUNTIME_PYTHON,integrityValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:[font]},explicitTotalSlideCount:10,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],verifyArtifactToolImport:true,receiptPath:path.join(build,'deck-validation.json')});
console.log(JSON.stringify(result));
