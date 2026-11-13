// Load Classification (Random Forest) - memanggil /api/classification/*
const $ = id => document.getElementById(id);
const pct = v => (v * 100).toFixed(1) + '%';
function setBig(el, text, cls){ el.textContent = text; el.className = 'big ' + cls; }

async function loadStatus(){
  try{
    const s = await (await fetch('/api/classification/status')).json();
    if(s.model_loaded){
      setBig($('model-status'), 'MODEL READY', 'ok');
      $('model-note').textContent = 'Random Forest siap digunakan.';
      setBig($('infer-status'), 'READY', 'ok');
    }
    if(s.metrics){
      $('m-acc').textContent = pct(s.metrics.accuracy);
      $('m-prec').textContent = pct(s.metrics.precision);
      $('m-rec').textContent = pct(s.metrics.recall);
      $('m-f1').textContent = pct(s.metrics.f1);
      document.querySelectorAll('.m .v').forEach(e => e.style.color = 'var(--ink)');
    }
  }catch(e){ $('model-note').textContent = 'Server tidak dapat dihubungi.'; }
}

$('btn-predict').addEventListener('click', async () => {
  const body = {voltage: $('in-voltage').value, power: $('in-power').value, power_factor: $('in-pf').value};
  try{
    const r = await fetch('/api/classification/predict', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
    const d = await r.json();
    if(!r.ok){ $('res-title').textContent = 'Gagal'; $('res-sub').textContent = d.error; return; }
    const bad = d.class_id === 1;
    setBig($('class-pred'), d.label.toUpperCase(), bad ? 'bad' : 'ok');
    $('res-title').textContent = d.label;
    $('res-sub').textContent = 'Keputusan Random Forest untuk data yang dimasukkan.';
    $('p-seimbang').textContent = pct(d.probability['Seimbang'] || 0);
    $('p-tidak').textContent = pct(d.probability['Tidak Seimbang'] || 0);
  }catch(e){ $('res-title').textContent = 'Gagal'; $('res-sub').textContent = 'Server tidak dapat dihubungi.'; }
});
loadStatus();
