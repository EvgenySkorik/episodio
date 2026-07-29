d = {"a": "b", "c": "d", "e": "c"}

def revert_dict2(dct: dict) -> dict:
    return  {v: k for k, v in dct.items()}

def revert_dict(dct: dict) -> dict:
    res = dict()
    for k, v in dct.items():
        res[v] = k
    return res


print(revert_dict(d))
print(revert_dict2(d))