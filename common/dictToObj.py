import inspect
import json
import logging

class obj(object):
    def __init__(self, d):
        for k, v in d.items():
            if isinstance(v, (list)):
                setattr(self, k, [obj(x) if isinstance(x, dict) else x for x in v])
            elif isinstance(v, (tuple)):
                setattr(self, k, tuple([obj(x) if isinstance(x, dict) else x for x in v]))
            else:
                setattr(self, k, obj(v) if isinstance(v, dict) else v)

    def __str__(self):
        attributes = ""
        members = dir(self)
        for member in members:
            if not(member.startswith('__') or member.endswith('__')):
                attr = getattr(self,member)
                if attributes != "":
                    attributes += ", "
                if not isinstance(attr, (list, tuple)):
                    if not isinstance(attr, (str)):
                        attributes += f"{member}={str(attr)}"
                    else:
                        attributes+= f"{member}='{str(attr)}'"
                else:
                    logging.debug("type of attribute:" + str(type(attr)))
                    attributes+= f"{member}="
                    attributes+= "[" if isinstance(attr, list) else "("
                    first = True
                    for a in attr:
                        if not first:
                            attributes+= ", "
                        attributes += str(a)
                        first = False
                    attributes += "]" if isinstance(attr, list) else ")"

        return f"<obj {attributes}>"

def objFromJson(filepath):
    o = None
    with open(filepath) as f:
        jsonStr = f.read()
        jsonData = json.loads(jsonStr)
        o = obj(jsonData)
        f.close()
    return o
    
def objToDict(o):
    d = {}
    for name in dir(o):
        if not name.startswith('__'):
            a = getattr(o, name)
            if isinstance(a, obj):
              d[name] = objToDict(a)
            elif isinstance(a, list):
                d[name] = []
                for e in a:
                    d[name].append(e if not isinstance(e, obj) else objToDict(e))
            elif isinstance(a, tuple):
                d[name] = ()
                for e in a:
                    d[name] += (e if not isinstance(e, obj) else objToDict(e),)
            else:
              d[name] = a
          
    return d

def objToJson(o, indent = 4):
    d = objToDict(o)
    j = json.dumps(d, indent=indent)

    return j

def objToJsonFile(o, filepath, indent = 4):
    jsonText = objToJson(o, indent)
    with open(filepath, "w") as f:
        f.write(jsonText)
        f.close()
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    d = {'a': 1, 'b': {'c': 2}, 'd': ["hi", {'foo': "bar"}], 'e': False, 'f': ('g', {'h': 'i'})}
    logging.debug(f"dict={d}")
    x = obj(d)
    print(str(x))
    print(x.b.c)
    print(x.d[1].foo)
    print(x.f)

    dd=objToDict(x)
    print(dd)
    jsonString = objToJson(x,2)
    print(f"objToJson:\n{jsonString}")
    ddd = json.loads(jsonString)
    print(f"{type(ddd)}={ddd}")

    o = fromJson("/var/radio/conf/radio.json")
    print(o)
