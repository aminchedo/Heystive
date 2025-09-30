import os, sys, csv, time, hashlib, json, collections
ROOT = os.getcwd()
DATE = time.strftime("%Y-%m-%d")
PLAN = f"archive_plan_{DATE}.csv"
reasons_map = {}
def add(rel, reason):
    reasons_map.setdefault(rel, set()).add(reason)
file_list = []
for dp, dn, fn in os.walk(ROOT):
    if ".git" in dp.split(os.sep):
        continue
    for f in fn:
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ROOT)
        st = os.stat(p)
        file_list.append((rel, st.st_size))
def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for ch in iter(lambda:f.read(1<<20), b""):
            h.update(ch)
    return h.hexdigest()
# rules
for rel, size in file_list:
    low = rel.lower()
    base = os.path.basename(rel).lower()
    if rel.endswith(".log") or "/.logs/" in ("/"+rel+"/"):
        add(rel, "log_artifact")
    if base == "heystive.db":
        add(rel, "runtime_db")
    if "backup" in low or "backups" in low:
        add(rel, "backup_copy")
    if rel.startswith("heystive_professional/legacy/") or rel.startswith("legacy/"):
        add(rel, "legacy_dup")
    if rel.startswith("enhancements/"):
        add(rel, "prototype_enhancement")
    if rel.startswith("api_bridge/"):
        add(rel, "unused_module_candidate")
    if rel.startswith("heystive_audio_output/") or rel.endswith(".mp3"):
        add(rel, "audio_output")
    if rel.startswith("templates/"):
        add(rel, "duplicate_template_copy")
    if base.endswith(".diff") or base == "safe_patches.diff":
        add(rel, "patch_diff")
    if base in ("branch_analysis.txt","branch_categorization.txt","archive_inventory_before_deletion.txt"):
        add(rel, "meta_note")
# duplicates
hmap = collections.defaultdict(list)
for rel, size in file_list:
    path = os.path.join(ROOT, rel)
    try:
        hmap[sha(path)].append(rel)
    except Exception:
        pass
for group in hmap.values():
    if len(group) < 2:
        continue
    keep = None
    for rel in sorted(group, key=lambda p: (p.count("/"), len(p))):
        if "legacy/" not in rel:
            keep = rel; break
    if keep is None:
        keep = sorted(group, key=lambda p: (p.count("/"), len(p)))[0]
    for rel in group:
        if rel != keep:
            add(rel, f"duplicate_of:{keep}")
rows = []
for rel, size in sorted(file_list):
    if rel in reasons_map:
        path = os.path.join(ROOT, rel)
        try:
            sh = sha(path)
        except Exception:
            sh = ""
        rows.append((rel, size, sh, ";".join(sorted(reasons_map[rel]))))
with open(PLAN, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["path","size_bytes","sha256","reasons"]); w.writerows(rows)
print(PLAN)