(function(){
  'use strict';
  const form=document.getElementById('sample-request-form');
  if(!form)return;
  const selected=new Set();
  const buttons=[...document.querySelectorAll('.product-option')];
  const hidden=document.getElementById('selected-products');
  const count=document.getElementById('selected-count');
  const productError=document.getElementById('product-error');
  const formError=document.getElementById('form-error');
  const submit=document.getElementById('sample-submit');

  function sync(){hidden.value=[...selected].join(', ');count.textContent=String(selected.size);productError.textContent='';}
  buttons.forEach(button=>button.addEventListener('click',()=>{
    const product=button.dataset.product;
    if(selected.has(product)){selected.delete(product);button.setAttribute('aria-pressed','false');}
    else if(selected.size<3){selected.add(product);button.setAttribute('aria-pressed','true');}
    else{productError.textContent='You can request up to three products at a time.';return;}
    sync();
  }));

  function payload(){const data={};new FormData(form).forEach((value,key)=>{data[key]=value;});data.products=[...selected].join(', ');data.lead_type='sample_request';return data;}
  async function send(data){
    if(window.JFTConversion)return window.JFTConversion.submitLead(data);
    const response=await fetch('https://api.web3forms.com/submit',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(data)});
    return response.json();
  }
  form.addEventListener('submit',async(event)=>{
    event.preventDefault();formError.textContent='';
    if(!selected.size){productError.textContent='Select at least one product for evaluation.';document.getElementById('product-grid').scrollIntoView({behavior:'smooth',block:'center'});return;}
    if(!form.checkValidity()){form.reportValidity();return;}
    submit.disabled=true;submit.querySelector('span').textContent='Sending request...';
    try{
      const result=await send(payload());
      if(!result||!result.success)throw new Error('Submission was not accepted');
      form.hidden=true;document.querySelector('.request-summary').hidden=true;
      const success=document.getElementById('form-success');
      document.getElementById('success-lead-id').textContent=result.lead_id||'JFT-SAMPLE';
      success.hidden=false;success.scrollIntoView({behavior:'smooth',block:'center'});
    }catch(error){
      console.error('Sample request submission failed:',error);
      formError.innerHTML='We could not record this request. Please retry, or <a href="https://wa.me/918425057274" target="_blank" rel="noopener">contact the sample desk on WhatsApp</a>.';
      submit.disabled=false;submit.querySelector('span').textContent='Retry sample request';
    }
  });
})();
