let ac=null, src=null, node=null, ws=null, started=false;
async function startMic(wsUrl){
  if(started) return;
  const stream = await navigator.mediaDevices.getUserMedia({audio:true});
  ac = new (window.AudioContext||window.webkitAudioContext)({latencyHint:"interactive"});
  await ac.audioWorklet.addModule("/static/mic-worklet.js");
  src = ac.createMediaStreamSource(stream);
  node = new AudioWorkletNode(ac, "mic-writer");
  node.port.onmessage = (ev)=>{
    const f32 = ev.data;
    const res = downsampleTo16k(f32, ac.sampleRate);
    const b = pcm16le(res);
    const b64 = btoa(String.fromCharCode.apply(null, new Uint8Array(b.buffer)));
    if(ws && ws.readyState===1){
      ws.send(JSON.stringify({type:"chunk", pcm_b64:b64}));
    }
  };
  src.connect(node);
  node.connect(ac.destination);
  ws = new WebSocket(wsUrl);
  ws.onopen = ()=>{
    ws.send(JSON.stringify({type:"start", sr:16000}));
  };
  ws.onmessage = (e)=>{
    const j = JSON.parse(e.data);
    if(window.HeystiveMic.onmessage){ window.HeystiveMic.onmessage(j); }
  };
  started = true;
}
function stopMic(){
  if(ws && ws.readyState===1) ws.send(JSON.stringify({type:"stop"}));
  if(node) node.disconnect();
  if(src) src.disconnect();
  if(ac) ac.close();
  ws=null; node=null; src=null; ac=null; started=false;
}
function downsampleTo16k(f32, inRate){
  const outRate = 16000;
  if(inRate===outRate) return f32;
  const ratio = inRate/outRate;
  const outLen = Math.floor(f32.length/ratio);
  const out = new Float32Array(outLen);
  for(let i=0;i<outLen;i++){
    const idx = Math.floor(i*ratio);
    out[i] = f32[idx];
  }
  return out;
}
function pcm16le(f32){
  const b = new ArrayBuffer(f32.length*2);
  const v = new DataView(b);
  let off=0;
  for(let i=0;i<f32.length;i++){
    let s = Math.max(-1, Math.min(1, f32[i]));
    v.setInt16(off, s<0?s*0x8000:s*0x7fff, true);
    off+=2;
  }
  return new Uint8Array(b);
}
window.HeystiveMic = {startMic, stopMic, onmessage:null};