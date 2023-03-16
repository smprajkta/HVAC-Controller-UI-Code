import json


PARAMS_KEY = "Params"
payload = {"Command": "set", "Seq": 4001, PARAMS_KEY: {"mode": 2, "temperature": 50, "fan": 1}}

cmd_dict = {"params_payload": {}}

print(payload["Command"])

print(len(payload[PARAMS_KEY]))

if len(payload[PARAMS_KEY]) in range(1, 4):
    if "mode" in payload[PARAMS_KEY].keys():
        print("True")
        if payload[PARAMS_KEY]["mode"] in range(3):
            print(payload[PARAMS_KEY]["mode"])
            cmd_dict["params_payload"]["mode"] = payload[PARAMS_KEY]["mode"]

    if "temperature" in payload[PARAMS_KEY].keys():
        cmd_dict["params_payload"]["temperature"] = payload[PARAMS_KEY]["temperature"]

    if "fan" in payload[PARAMS_KEY].keys():
        print("True")
        if payload[PARAMS_KEY]["fan"] in range(2):
            print(payload[PARAMS_KEY]["fan"])
            cmd_dict["params_payload"]["fan"] = payload[PARAMS_KEY]["fan"]

else:
    print("None")

print(cmd_dict)
