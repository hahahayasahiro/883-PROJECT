import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const workspaceDir=path.resolve(import.meta.dirname,'..');
const dep=process.env.CAMPUS_RUNTIME_MODULES;process.env.RUNTIME_NODE_MODULES=dep;
const {PresentationFile,FileBlob}=await import(pathToFileURL(path.join(dep,'@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const skill=process.env.CAMPUS_SLIDE_SKILL,python=process.env.CAMPUS_RUNTIME_PYTHON;
const out=path.join(workspaceDir,'deliverables'),build=path.join(workspaceDir,'.build','enhanced-presentation-validated');await fs.mkdir(build,{recursive:true});
const source=path.join(out,'SmartCampus-progress-12min.pptx');
const sourceSha=crypto.createHash('sha256').update(await fs.readFile(source)).digest('hex');
const p=await PresentationFile.importPptx(await FileBlob.load(source));
const notes=(await fs.readFile(path.join(out,'SPEAKER_NOTES_ENHANCED.md'),'utf8')).split(/^## /m).slice(1);
if(notes.length!==13||p.slides.items.length!==13)throw Error('Expected 13 slides and matching notes');
function set(n,index,value){p.slides.items[n-1].shapes.items[index].text=value;}
function groups(n,data){for(let i=0;i<data.length;i++){set(n,3+i*2,data[i][0]);set(n,4+i*2,data[i][1]);}}
set(2,3,'Six connected modules now support saved, editable and traceable workflows.');
groups(3,[['Current progress','Saved conversations, follow-up questions and expandable source excerpts.'],['Verified integration','Live DeepSeek calls and service shortcuts with explicit user actions.'],['Next action','Evaluate retrieval coverage and claim-level source support.']]);
set(4,0,'Interests, Suggestions and Semester Plans');
groups(4,[['Interest-based rules','Save goals and rank eligible foundations for your chosen direction.'],['Saved plan','Add or remove courses and track a synthetic 12-credit limit.'],['Current result','Prerequisites and duplicate-course restrictions remain enforced.']]);
groups(5,[['Implemented and checked','Interest preferences, saved plans, prerequisite restrictions and credit limits.'],['Current limitations','Rule-based ranking over synthetic profiles. No timetable optimisation or trained risk model.'],['Next work','Broaden profiles and evaluate recommendations against the transparent rule baseline.']]);
set(6,0,'Room Search and Editable Reservations');
groups(6,[['Find a space','Filter by time, capacity, type and equipment; inspect the timetable.'],['Resolve conflicts','Choose an available alternative or modify your own reservation.'],['Keep a record','Cancelled bookings retain their reason and remain in history.']]);
set(7,0,'Fault Classification and Shared Integration');
groups(7,[['AI suggestion','DeepSeek suggests category and priority; the user confirms the report.'],['Preserved records','Versioned database migration retains earlier campus data.'],['Next action','Verify a second installation and coordinate shared interface changes.']]);
groups(8,[['Repair history','Filter work, set an ETA, add notes and record expenses.'],['Evidence','The ticket keeps status changes and cost adjustments.'],['Energy boundaries','Filter persisted simulated readings by room and date. No real control.']]);
groups(9,[['Available local evidence','34 backend cases cover migration, isolation, file boundaries and connected workflows.'],['Checks still needed','Broader AI accuracy, a second physical computer and classroom-device rehearsal.'],['Next work','Keep a stable release and rehearse one new workflow per speaker within two minutes.']]);
set(10,10,'Acceptance focus: persistent operations, shared histories and validated AI integration.');
set(10,11,'Rules and simulated energy stay explicit. Live AI is connected; broader evaluation remains next.');
set(11,0,'Material Upload, Evidence and Review Versions');
groups(11,[['Material workflow','Upload TXT or text PDF; confirm selected AI-extracted fields.'],['Evidence and versions','Inspect findings and corrections; preserve outdated reviews by version.'],['Next evaluation','Test subtle contradictions. OCR and automatic approval remain out of scope.']]);
set(12,0,'Correction Requests and In-app Notifications');
groups(12,[['Current progress','Search applications, read notifications and follow status changes.'],['Correction loop','Staff return a submission; students save a revision and resubmit.'],['Access boundary','Private student records and staff-only decision actions.']]);
set(13,0,'Processing Timeline and Delivery Plan');
groups(13,[['Connected evidence','Submission, return, revision, resubmission and approval share a timeline.'],['Current limitations','In-app updates after refresh. No emails or per-staff workload allocation.'],['Next action','Evaluate usability and rehearse the verified release on presentation equipment.']]);
const images={3:'conversation-focus',4:'learning-focus',6:'booking-focus',7:'classification-focus',8:'maintenance-focus',11:'versions-focus',12:'notification-focus',13:'timeline-focus'};
for(let i=0;i<13;i++){
 const s=p.slides.items[i];s.speakerNotes.text=notes[i];
 if(images[i+1]){const file=images[i+1]+'.png';const bytes=await fs.readFile(path.join(out,'enhanced-screenshots',file));const img=s.images.items[0];const frame=img.frame,fit=img.fit;img.replace({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt:'Actual enhanced-system browser capture '+file});const iw=bytes.readUInt32BE(16),ih=bytes.readUInt32BE(20),scale=Math.min(665/iw,415/ih);img.frame={left:555+(665-iw*scale)/2,top:210+(415-ih*scale)/2,width:iw*scale,height:ih*scale};img.crop={left:0,top:0,right:0,bottom:0};img.fit='contain';s.speakerNotes.text+='\nEvidence: enhanced-screenshots/'+file+'. All campus data is synthetic. The displayed AI mode is the actual recorded mode.';}
 const png=await p.export({slide:s,format:'png',scale:1});await fs.writeFile(path.join(build,'slide-'+(i+1)+'.png'),new Uint8Array(await png.arrayBuffer()));
}
const total=notes.reduce((sum,n)=>sum+Number(n.split('\n')[0].match(/(\d+) seconds/)?.[1]||0),0);if(total!==720)throw Error('Timing must total 720 seconds.');
const candidatePath=path.join(build,'candidate.pptx');await (await PresentationFile.exportPptx(p)).save(candidatePath);
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({workspaceDir,candidatePath,finalPath:path.join(out,'SmartCampus-enhanced-presentation.pptx'),pythonExecutable:python,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],fontPolicy:{basis:'reference',families:['Arial'],referencePath:source,referenceSha256:sourceSha},explicitTotalSlideCount:13,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],verifyArtifactToolImport:true,receiptPath:path.join(build,'validation.json')});
console.log(JSON.stringify({finalPath:result.finalPath,slides:13,seconds:total}));
