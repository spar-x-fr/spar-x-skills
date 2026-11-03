import json, re, sys
answer = open(sys.argv[1], encoding="utf-8").read()
found = re.findall(r"\{[^{}]*\"value\"[^{}]*\}", answer)
try:
    data = json.loads(found[-1])
    ok = abs(float(data["value"]) - 1.7) < 1e-9 and data["file"].replace("\\", "/").lstrip("./") == "payments/client.py"
except Exception as err:
    print("unparsable:", err); sys.exit(1)
print("pass" if ok else f"wrong: {data}"); sys.exit(0 if ok else 1)
