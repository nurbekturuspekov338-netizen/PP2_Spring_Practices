import json

with open(r"sample-data.json", "r") as f:
    data=json.load(f)
    
print("Interface Status")
print("="*80)
print(f"{'DN':50} {'Description':20} {'Speed':8} {'MTU':6}")
print("-" * 80)
for item in data["imdata"]:
    atr=item["l1PhysIf"]["attributes"]
    
    dn=atr.get("dn", "")
    descr = atr.get("descr", "")
    speed = atr.get("speed", "")
    mtu = atr.get("mtu", "")
    print(f"{dn:50} {descr:20} {speed:8} {mtu:6}")
