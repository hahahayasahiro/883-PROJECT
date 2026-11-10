import {api,esc,heading,wire,$,user,toast,bind} from '/shared.js';
export async function render(root){
 const conversations=await api('/assistant/conversations');
 const key='conversation-'+user.id;
 let cid=Number(localStorage.getItem(key))||conversations[0]?.id;
 if(!conversations.some(c=>c.id===cid))cid=null;
 const history=cid?await api('/assistant/conversations/'+cid):[];
 root.innerHTML=heading('LEARNING / 01','Study assistant','Conversations with evidence and campus-service shortcuts.','AI assisted')+
 '<div class="two-col"><section class="card"><h3>Your conversations</h3><div class="actions"><select id="conversation"><option value="">Choose a conversation</option>'+conversations.map(c=>'<option value="'+c.id+'">'+esc(c.title)+'</option>').join('')+'</select><button id="new-chat" class="secondary">New conversation</button></div><h3>Ask a follow-up</h3><form id="question"><label>Your question<textarea name="question" minlength="3" maxlength="1200" required placeholder="What are the prerequisites for CS202?"></textarea></label><button>Ask assistant</button></form><h3>Quick questions</h3><div class="actions">'+['What are the prerequisites for CS202?','What are the room booking rules?','How do I apply for a transcript?','What are the library opening hours?'].map(q=>'<button class="small secondary faq" data-question="'+esc(q)+'">'+esc(q)+'</button>').join('')+'</div><div class="notice">Each turn retrieves fresh evidence. Only the latest ten previous turns are supplied as conversation context. Service shortcuts never submit an action automatically.</div></section><section class="card"><h3>Conversation & sources</h3><div id="reply"></div></section></div>';
 $('#conversation').value=cid||'';
 const display=items=>{$('#reply').innerHTML=items.map(r=>'<article class="chat-turn"><h3>'+esc(r.question)+'</h3><p class="tag">'+esc(r.mode)+'</p><p class="answer">'+esc(r.answer)+'</p>'+r.sources.map(s=>'<details class="source"><summary>['+esc(s.id)+'] '+esc(s.title)+'</summary><p>'+esc(s.body)+'</p></details>').join('')+(r.links||[]).map(l=>'<a class="service-link" href="#'+esc(l.page)+'">'+esc(l.label)+' ↗</a>').join('')+'</article>').join('')||'<p class="muted">Start a conversation or select a saved one.</p>';};
 display(history);
 $('#conversation').onchange=async e=>{try{cid=Number(e.target.value)||null;if(cid){localStorage.setItem(key,cid);display(await api('/assistant/conversations/'+cid));}else display([]);}catch(e){toast(e.message);}};
 $('#new-chat').onclick=async()=>{try{cid=(await api('/assistant/conversations','POST')).id;localStorage.setItem(key,cid);await render(root);}catch(e){toast(e.message);}};
 bind('.faq',async b=>{$('#question textarea').value=b.dataset.question;$('#question textarea').focus();});
 wire('#question',async f=>{const text=f.get('question');const r=await api('/assistant','POST',{question:text,conversation_id:cid});cid=r.conversation_id;localStorage.setItem(key,cid);await render(root);$('#reply .chat-turn:last-child')?.scrollIntoView({block:'nearest'});});
}
