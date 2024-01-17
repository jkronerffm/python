import inspect

class dictToObj(object):
    def __init__(self, d):
        for k, v in d.items():
            if isinstance(v, (list, tuple)):
                setattr(self, k, [dictToObj(x) if isinstance(x, dict) else x for x in v])
            else:
                setattr(self, k, dictToObj(v) if isinstance(v, dict) else v)

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
                    attributes+= f"{member}=["
                    first = True
                    for a in attr:
                        if not first:
                            attributes+= ", "
                        attributes += str(a)
                        first = False
                    attributes += "]"

        return f"<obj {attributes}>"


if __name__ == "__main__":
    d = {'a': 1, 'b': {'c': 2}, 'd': ["hi", {'foo': "bar"}], 'e': False}

    x = dictToObj(d)
    print(str(x))
    print(x.b.c)
    print(x.d[1].foo)
          
