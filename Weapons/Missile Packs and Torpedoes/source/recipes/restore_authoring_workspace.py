from pathlib import Path
import shutil,sys,json
source=Path(__file__).resolve().parents[1]
dest=Path(sys.argv[1]).expanduser().resolve()
assert not dest.exists(), "Choose a new directory; do not overwrite ongoing art"
dest.mkdir(parents=True)
shutil.copytree(source,dest/"source")
shutil.copytree(source/"resources",dest/"resources")
for p in source.glob("*.blend"):shutil.copy2(p,dest/p.name)
(dest/"maps").mkdir()
for p in (source/"resources").glob("*.png"):
    name=p.name.split("_",1)[1] if len(p.name.split("_",1)[0])==12 else p.name
    if name.startswith("ordnance_"):shutil.copy2(p,dest/"maps"/name)
for r in json.loads((source/"snapshot_v3.json").read_text())["resources"]:
    p=source.parent/r["path"]
    name=p.name.split("_",1)[1]
    if name.startswith("ordnance_"):shutil.copy2(p,dest/"maps"/name)
scene=dest/"ordnance_worn_audit_v3.blend"
(dest/"project_state.json").write_text(json.dumps({"latest_scene":str(scene),"active_uv_map":"Ordnance_Delivery_UV_v3","emissives":"deferred","release_status":"hold"},indent=2)+"\n")
print(scene)
