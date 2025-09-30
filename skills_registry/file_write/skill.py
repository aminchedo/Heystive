import sys, json, os, time, pathlib
if len(sys.argv)<2:
    print(json.dumps({"ok":False,"error":"no_input"}))
    sys.exit(1)
data = json.loads(open(sys.argv[1],"r",encoding="utf-8").read())
text = data.get("text","")
outdir = "sandbox_output"
pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
fname = str(int(time.time()*1000)) + ".txt"
path = os.path.join(outdir, fname)
open(path,"w",encoding="utf-8").write(text)
print(json.dumps({"ok":True,"path":path}))