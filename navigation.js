(()=>{
const root=document.getElementById('mp-motion');
const menu=root.querySelector('#mp-menu'),nav=root.querySelector('#mp-nav');
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
function closeMenu(){nav.classList.remove('open');menu.setAttribute('aria-expanded','false');menu.setAttribute('aria-label','Open navigation');}
menu.onclick=()=>{const open=nav.classList.toggle('open');menu.setAttribute('aria-expanded',String(open));menu.setAttribute('aria-label',open?'Close navigation':'Open navigation');};
root.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav.classList.contains('open')){closeMenu();menu.focus();}});
document.addEventListener('click',e=>{if(!e.target.closest('#mp-motion header'))closeMenu();});
const mobile=matchMedia('(max-width:700px)');mobile.addEventListener('change',closeMenu);
root.addEventListener('click',e=>{
 const link=e.target.closest('a[href^="#mp-"]');if(!link)return;
 const target=document.getElementById(link.hash.slice(1));if(!target)return;
 e.preventDefault();closeMenu();history.pushState(null,'',link.hash);
 target.setAttribute('tabindex','-1');target.focus({preventScroll:true});
 requestAnimationFrame(()=>target.scrollIntoView({behavior:reduced.matches?'instant':'smooth',block:'start'}));
});
root.querySelector('#mp-form').onsubmit=e=>{e.preventDefault();root.querySelector('#mp-form-status').textContent='Preview only — no email has been submitted.';};
if(!reduced.matches&&'IntersectionObserver'in window){
 const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('is-visible');observer.unobserve(entry.target);}}),{threshold:.08});
 root.querySelectorAll('.section h2,.section .photo,.section blockquote').forEach(el=>{el.classList.add('reveal-ready');observer.observe(el);});
}
})();
