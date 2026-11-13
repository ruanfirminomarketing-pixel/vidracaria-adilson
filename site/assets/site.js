(function(){
  var d=document, w=window; w.dataLayer=w.dataLayer||[];
  // se a foto não carregar, usa a ilustração local
  function swapImg(i){if(i.dataset.fb&&!i.dataset.fbd){i.dataset.fbd=1;i.removeAttribute('srcset');i.src=i.dataset.fb}}
  d.querySelectorAll('img[data-fb]').forEach(function(i){if(i.complete&&i.naturalWidth===0)swapImg(i);else i.addEventListener('error',function(){swapImg(i)})});
  // UTMs do primeiro acesso: guardadas para acompanhar a origem das conversões
  try{var q=new URLSearchParams(location.search),u={};['utm_source','utm_medium','utm_campaign','utm_content','utm_term','gclid'].forEach(function(k){if(q.get(k))u[k]=q.get(k)});
    if(Object.keys(u).length&&!localStorage.getItem('va_utm'))localStorage.setItem('va_utm',JSON.stringify(u))}catch(e){}
  function utm(){try{return JSON.parse(localStorage.getItem('va_utm')||'{}')}catch(e){return{}}}
  function push(ev,extra){var o={event:ev,page_type:d.body.dataset.type||'',service:d.body.dataset.service||'',page_path:location.pathname};var u=utm();for(var k in u)o[k]=u[k];for(var k2 in (extra||{}))o[k2]=extra[k2];w.dataLayer.push(o)}
  // cliques no WhatsApp e no telefone
  d.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a');if(!a)return;var h=a.getAttribute('href')||'';
    if(h.indexOf('https://wa.me/')===0)push('whatsapp_click',{cta_location:a.dataset.loc||''});
    else if(h.indexOf('tel:')===0)push('phone_click',{cta_location:a.dataset.loc||''});});
  // menu de serviços (desktop): abre também com clique e teclado
  var dd=d.querySelector('.has-dd'),btn=dd&&dd.querySelector('.dd-btn');
  if(btn){btn.addEventListener('click',function(){var o=dd.classList.toggle('open');btn.setAttribute('aria-expanded',o)});
    d.addEventListener('click',function(e){if(!dd.contains(e.target)){dd.classList.remove('open');btn.setAttribute('aria-expanded','false')}});
    d.addEventListener('keydown',function(e){if(e.key==='Escape'){dd.classList.remove('open');btn.setAttribute('aria-expanded','false')}});}
  // menu celular
  var dr=d.getElementById('drawer'),ob=d.querySelector('.burger');
  function setDr(o){dr.classList.toggle('open',o);ob.setAttribute('aria-expanded',o);d.body.style.overflow=o?'hidden':'';if(o)dr.querySelector('.x').focus()}
  if(dr&&ob){ob.addEventListener('click',function(){setDr(true)});dr.querySelector('.x').addEventListener('click',function(){setDr(false)});
    dr.addEventListener('click',function(e){if(e.target===dr)setDr(false)});d.addEventListener('keydown',function(e){if(e.key==='Escape')setDr(false)});}
  // filtro do blog
  var fb=d.querySelectorAll('.filters button');fb.forEach(function(b){b.addEventListener('click',function(){var c=b.dataset.cat;fb.forEach(function(x){x.setAttribute('aria-pressed',x===b)});
    d.querySelectorAll('[data-cat]').forEach(function(p){if(p.tagName!=='BUTTON')p.hidden=!(c==='*'||p.dataset.cat===c)})})});
  // formulário de orçamento: monta a mensagem e abre o WhatsApp
  var f=d.getElementById('orcamento');
  if(f){var tel=f.querySelector('[name=telefone]');
    tel.addEventListener('input',function(){var v=tel.value.replace(/\D/g,'').slice(0,11);var o=v;if(v.length>2)o='('+v.slice(0,2)+') '+v.slice(2);if(v.length>7)o='('+v.slice(0,2)+') '+v.slice(2,v.length-4)+'-'+v.slice(-4);tel.value=o});
    f.addEventListener('submit',function(e){e.preventDefault();var g=function(n){return(f.querySelector('[name='+n+']').value||'').trim()},err=f.querySelector('.err');
      var nome=g('nome'),fone=g('telefone').replace(/\D/g,''),serv=g('servico'),bairro=g('bairro'),msg=g('mensagem');
      if(nome.length<2){err.textContent='Informe seu nome.';return}
      if(fone.length<10){err.textContent='Informe um telefone com DDD.';return}
      if(!serv){err.textContent='Escolha o serviço.';return}
      if(!bairro){err.textContent='Informe o bairro.';return}
      err.textContent='';
      var t='Olá! Encontrei o site da Vidraçaria do Adilson e gostaria de solicitar um orçamento.\n\nNome: '+nome+'\nTelefone: '+g('telefone')+'\nServiço: '+serv+'\nBairro: '+bairro+(msg?'\nDetalhes: '+msg:'');
      push('generate_lead',{form_name:'orcamento',form_service:serv,form_bairro:bairro});
      var url='https://wa.me/5521987576554?text='+encodeURIComponent(t);var win=w.open(url,'_blank');if(!win)location.href=url;
      f.querySelector('.ok').hidden=false;});}
})();