(function(){
  var k="heystive_theme";function a(t){document.documentElement.setAttribute("data-theme",t)}
  var c=localStorage.getItem(k)||"light";a(c);
  var b=document.getElementById("theme-toggle");
  if(b){b.addEventListener("click",function(){c=c==="light"?"dark":"light";localStorage.setItem(k,c);a(c)})}
})();