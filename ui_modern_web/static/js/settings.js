(function(){
  var f=document.getElementById("settings-form");
  function get(id){return document.getElementById(id)}
  function fromList(t){return t.split("\n").map(function(x){return x.trim()}).filter(Boolean)}
  function toList(a){return (a||[]).join("\n")}
  function load(){
    fetch("/api/settings").then(function(r){return r.json()}).then(function(s){
      get("theme").value=s.theme;
      get("stt_engine").value=s.stt_engine;
      get("tts_engine").value=s.tts_engine;
      get("llm_engine").value=s.llm_engine;
      get("llm_model_path").value=s.llm_model_path;
      get("hotkey_toggle").value=s.hotkey_toggle;
      get("os_whitelist_paths").value=toList(s.os_whitelist_paths);
      get("os_whitelist_apps").value=toList(s.os_whitelist_apps);
      get("log_level").value=s.log_level;
      document.documentElement.setAttribute("data-theme",s.theme);
      localStorage.setItem("heystive_theme",s.theme);
    });
  }
  f.addEventListener("submit",function(e){
    e.preventDefault();
    var payload={
      theme:get("theme").value,
      stt_engine:get("stt_engine").value,
      tts_engine:get("tts_engine").value,
      llm_engine:get("llm_engine").value,
      llm_model_path:get("llm_model_path").value,
      hotkey_toggle:get("hotkey_toggle").value,
      os_whitelist_paths:fromList(get("os_whitelist_paths").value),
      os_whitelist_apps:fromList(get("os_whitelist_apps").value),
      log_level:get("log_level").value,
      allow_origins:["http://127.0.0.1:8765","http://localhost:8765"]
    };
    fetch("/api/settings",{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)})
      .then(function(r){return r.json()})
      .then(function(_){load()});
  });
  load();
})();