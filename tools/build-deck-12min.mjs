import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';

const workspaceDir=path.resolve(import.meta.dirname,'..');
const dep=process.env.CAMPUS_RUNTIME_MODULES;
if(!dep)throw Error('Set CAMPUS_RUNTIME_MODULES to the supplied runtime package directory.');
process.env.RUNTIME_NODE_MODULES=dep;
const {PresentationFile,FileBlob}=await import(pathToFileURL(path.join(dep,'@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const SKILL_DIR=process.env.CAMPUS_SLIDE_SKILL;
const RUNTIME_PYTHON=process.env.CAMPUS_RUNTIME_PYTHON;
const out=path.join(workspaceDir,'deliverables');
const build=path.join(workspaceDir,'.build','progress-12min');
await fs.mkdir(build,{recursive:true});
const sourcePath=path.join(out,'SmartCampus-progress.pptx');
const sourceBytes=await fs.readFile(sourcePath);
const originalHash=crypto.createHash('sha256').update(sourceBytes).digest('hex');
const presentation=await PresentationFile.importPptx(await FileBlob.load(sourcePath));
const sourceInspection=await presentation.inspect({kind:'slide,layout,textbox,image',maxChars:50000});
await fs.writeFile(path.join(build,'source-inspection.ndjson'),sourceInspection.ndjson);
for(let i=0;i<presentation.slides.items.length;i++){
 const png=await presentation.export({slide:presentation.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(build,`source-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
}
// Keep and edit the actual original cover. Replace content slides for the new structure.
presentation.slides.delete([1,2,3,4,5,6,7,8,9]);
const notes=await fs.readFile(path.join(out,'SPEAKER_NOTES_12MIN.md'),'utf8');
const noteSections=notes.split(/^## /m).slice(1);
if(noteSections.length!==13)throw Error('Expected 13 speaker-note sections.');
const font='Arial';
function text(s,value,x,y,w,h,size=26,color='#163d36',bold=false){
 const shape=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 shape.text=value;shape.text.style={fontFamily:font,fontSize:size,color,bold};return shape;
}
function slide(title,owner,seconds){
 const s=presentation.slides.add();const n=presentation.slides.items.length;
 s.background.fill='#f5f7f4';
 text(s,title,64,52,1152,98,42,'#163d36',true);
 text(s,`${owner}    /    ${seconds} seconds`,64,165,1152,40,22,'#6b8177');
 text(s,`SmartCampus progress     ${String(n).padStart(2,'0')} / 13`,64,670,1152,24,14,'#6b8177');
 s.speakerNotes.text=noteSections[n-1];return s;
}
function paragraph(s,label,body,y,x=64,w=1120){text(s,label,x,y,w,36,26,'#136c60',true);text(s,body,x,y+44,w,76,25);}
async function screenshot(s,file){
 const bytes=await fs.readFile(path.join(out,'screenshots',file));
 s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt:`Actual prototype screenshot: ${file}. AI modes remain as recorded.`,fit:'contain',position:{left:555,top:210,width:665,height:415}});
 s.speakerNotes.text+=`\nEvidence: local browser capture deliverables/screenshots/${file}; synthetic data. No live AI verification implied.`;
}
function compact(s,label,body,y){text(s,label,64,y,455,32,23,'#136c60',true);text(s,body,64,y+37,455,93,25);}
const cover=presentation.slides.items[0];
for(const sh of cover.shapes.items){if(String(sh.text)==='Working prototype')sh.text='Progress presentation';if(String(sh.text).startsWith('SmartCampus prototype'))sh.text='SmartCampus progress     01 / 13';}
cover.speakerNotes.text=noteSections[0];
let s=slide('Project Goals and Team Responsibilities','Rongkai Cheng',50);
text(s,'One local prototype connects learning, facilities and administration.',64,225,1145,70,30,'#163d36',true);
const responsibilities=[
 'Rongkai Cheng: study assistant and shared AI service',
 'Dequn Shang: learning suggestions and support rules',
 'Jun Yang: booking, fault reporting and system integration',
 'Lexi Shu: maintenance, simulated energy and QA',
 'Zheyuan Huai: requirements, scope and document pre-review',
 'Shiran Yuan: service portal and shared user interface',
];
responsibilities.forEach((line,i)=>text(s,line,64,325+i*44,1152,39,25));
text(s,'Revised team responsibilities. All campus records and policies are fictional.',64,615,1152,35,20,'#6b8177');
s=slide('Study Assistant and Shared AI Service','Rongkai Cheng',70);
compact(s,'Current progress','Local retrieval and a shared DeepSeek adapter are implemented.',225);
compact(s,'Current problem','Real model access and answer quality remain unverified.',365);
compact(s,'Next action','Verify both AI features and evaluate cited answer support.',505);
await screenshot(s,'03-assistant.png');
s=slide('Learning Path and Support Rules','Dequn Shang',50);
compact(s,'Eligibility','Suggest courses when prerequisites have been passed.',225);
compact(s,'Support reminder','Mark below 50 or attendance below 75% triggers an explanation.',365);
compact(s,'Current result','Stored records drive the suggestions shown on the page.',505);
await screenshot(s,'04-learning.png');
s=slide('Learning Progress, Problems and Next Steps','Dequn Shang',70);
paragraph(s,'Implemented and locally checked','Prerequisite exclusions and low-performance reminders use explicit rules.',225);
paragraph(s,'Current limitations','Small synthetic profiles. No trained risk model or interest-based course ranking.',365);
paragraph(s,'Next work','Broaden profiles and boundary tests, then compare richer methods against the rules.',505);
s=slide('Spaces, Bookings and Fault Reports','Jun Yang',50);
compact(s,'Current progress','Reserve and cancel your own room slot, with overlap rejection.',225);
compact(s,'Shared workflow','A fault report creates a ticket in the maintenance queue.',365);
compact(s,'Scope boundary','No occupancy prediction or AI fault classification yet.',505);
await screenshot(s,'05-booking-conflict.png');
s=slide('Integration Progress and Remaining Work','Jun Yang',70);
compact(s,'Verified connection','Fault intake and maintenance read the same saved tickets.',225);
compact(s,'Current problem','Second-machine setup and the team repository are pending.',365);
compact(s,'Next action','Verify installation, coordinate schema changes and merge by module.',505);
await screenshot(s,'06-student-tickets.png');
s=slide('Maintenance Workflow and Energy Demonstration','Lexi Shu',50);
compact(s,'Current progress','Staff advance repair tickets and record the maintenance cost.',225);
compact(s,'Current evidence','The queue shows open and completed work.',365);
compact(s,'Scope boundary','Energy is simulated. No physical control or failure prediction.',505);
await screenshot(s,'10-maintenance.png');
s=slide('Verification, Problems and Next Steps','Lexi Shu',70);
paragraph(s,'Available local evidence','12 backend cases passed. Browser workflows and real server-restart persistence checked.',225);
paragraph(s,'Checks still needed','Real DeepSeek service, a second computer and the classroom display remain unverified.',365);
paragraph(s,'Next work','Recheck changes, record defects, freeze features and rehearse recovery within each slot.',505);
s=slide('System Requirements and Prototype Scope','Zheyuan Huai',50);
text(s,'System Analyst and Document Pre-review Lead',64,212,1152,40,26,'#136c60',true);
const domains=[
 ['Learning support','M1.1 Study assistant\nM1.2 Learning path and support reminders'],
 ['Facilities and resources','M2.1 Booking and fault reports\nM2.2 Energy and maintenance'],
 ['Administrative services','M3.1 Document pre-review\nM3.2 Service portal and tracking'],
];
domains.forEach(([label,body],i)=>{text(s,label,64,280+i*90,380,65,26,'#136c60',true);text(s,body,460,280+i*90,755,78,25);});
text(s,'Acceptance focus: usable workflows, shared records and two AI integration paths.',64,565,1152,40,25,'#163d36',true);
text(s,'Rules and simulated readings are explicit. Live AI verification and advanced features remain pending.',64,613,1152,42,20,'#6b8177');
s=slide('Intelligent Document Pre-review','Zheyuan Huai',70);
compact(s,'Implemented correction loop','Save draft, check rules, request AI analysis, correct and re-review.',225);
compact(s,'Concrete evidence','Student S1001 versus material S9999: the rule flags the conflict.',365);
compact(s,'Problem and next work','Verify live AI and test text contradictions. Staff retain approval.',505);
await screenshot(s,'07-review-issue.png');
s=slide('Service Portal and Application Tracking','Shiran Yuan',50);
compact(s,'Current progress','Students submit drafts and track their own applications.',225);
compact(s,'Shared workflow','The portal reuses saved drafts and pre-review results.',365);
compact(s,'Access boundary','Only administrative staff decide submitted applications.',505);
await screenshot(s,'09-submitted.png');
s=slide('Approval Evidence and Delivery Plan','Shiran Yuan',70);
compact(s,'Current evidence','Students see the saved staff decision and explanation after refresh.',225);
compact(s,'Current limitations','No email delivery or per-staff workload allocation.',365);
compact(s,'Next action','Improve status clarity, test rejection cases and rehearse delivery.',505);
await screenshot(s,'12-student-approved.png');
s.speakerNotes.text+='\nClassroom presentation: 12 Nov 2026 during Tutorial. Group leader submits to Moodle by 23:59, 13 Nov 2026. Source: assignment screenshot supplied in this chat.';
if(presentation.slides.items.length!==13)throw Error('Incorrect slide count');
const timing=noteSections.map((section,i)=>({slide:i+1,heading:section.split('\n')[0],seconds:Number(section.split('\n')[0].match(/(\d+) seconds/)?.[1]||0)}));
if(timing.reduce((sum,x)=>sum+x.seconds,0)!==720)throw Error('Expected 720 total seconds.');
for(let i=1;i<13;i+=2)if(timing[i].seconds+timing[i+1].seconds!==120)throw Error('Each member must have 120 seconds.');
await fs.writeFile(path.join(build,'timing-check.json'),JSON.stringify(timing,null,2));
for(let i=0;i<13;i++){const png=await presentation.export({slide:presentation.slides.items[i],format:'png',scale:1});await fs.writeFile(path.join(build,`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));}
const candidatePath=path.join(build,'candidate.pptx');await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL_DIR,'container_tools/artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({workspaceDir,candidatePath,finalPath:path.join(out,'SmartCampus-progress-12min.pptx'),pythonExecutable:RUNTIME_PYTHON,integrityValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'reference',families:[font],referencePath:sourcePath,referenceSha256:originalHash},explicitTotalSlideCount:13,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],verifyArtifactToolImport:true,receiptPath:path.join(build,'deck-validation.json')});
if(crypto.createHash('sha256').update(await fs.readFile(sourcePath)).digest('hex')!==originalHash)throw Error('Original deck changed.');
console.log(JSON.stringify({finalPath:result.finalPath,slides:13,totalSeconds:720,originalPreserved:true}));
