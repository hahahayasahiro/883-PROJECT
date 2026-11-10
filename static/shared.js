export const $ = s => document.querySelector(s);
export const esc = s => String(s ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export let user;
export function setUser(value){user=value;}
export async function api(path,method='GET',body){
  const r=await fetch('/api'+path,{method,headers:body?{'Content-Type':'application/json'}:{},body:body?JSON.stringify(body):undefined});
  let data;try{data=await r.json();}catch{throw Error('Server returned an unreadable response.');}
  if(!r.ok){if(r.status===401&&path!='/auth/login'){setUser(null);window.dispatchEvent(new Event('signedout'));}const err=Error(typeof data.detail==='string'?data.detail:data.detail?.message||JSON.stringify(data.detail));err.detail=data.detail;throw err;}return data;
}
export function toast(message){$('#toast').textContent=message;$('#toast').hidden=false;clearTimeout(window.toastTimer);window.toastTimer=setTimeout(()=>$('#toast').hidden=true,6500);}
export function heading(label,title,subtitle,tag='Prototype'){return `<div class="page-heading"><div><p class="eyebrow">${label}</p><h1>${title}</h1><p>${subtitle}</p></div><span class="tag">${tag}</span></div>`;}
export function empty(text){return `<div class="empty">${esc(text)}</div>`;}
export function wire(form,fn){const element=$(form);if(!element)return;element.onsubmit=async e=>{e.preventDefault();const button=element.querySelector('button[type="submit"],button:not([type])');if(button)button.disabled=true;try{await fn(new FormData(element));}catch(err){toast(err.message);}finally{if(button)button.disabled=false;}};}
export async function render(){window.dispatchEvent(new Event('campusrefresh'));}
export async function upload(file){const form=new FormData();form.append('file',file);const r=await fetch('/api/reviews/upload',{method:'POST',body:form});const d=await r.json();if(!r.ok)throw Error(d.detail||'Upload failed.');return d;}
export function bind(selector,fn){document.querySelectorAll(selector).forEach(b=>b.onclick=async()=>{b.disabled=true;try{await fn(b);}catch(e){toast(e.message);}finally{b.disabled=false;}});}
export function dateText(value){return value?new Date(value.includes('T')?value:value.replace(' ','T')+'Z').toLocaleString():'Not recorded';}
