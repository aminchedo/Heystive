class MicWriter extends AudioWorkletProcessor{
  process(inputs, outputs, params){
    const ch = inputs[0][0];
    if(ch && ch.length>0){
      this.port.postMessage(ch.slice(0));
    }
    return true;
  }
}
registerProcessor("mic-writer", MicWriter);