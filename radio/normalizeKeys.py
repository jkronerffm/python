def normalizeKeys(d):
    changed = {}
    for name, value in d.items():
        if name[:1] == '@':
            changedName = name[1:]
        else:
            changedName = name
        if type(value) == dict:
            changed[changedName] = normalizeKeys(value)
        elif type(value) == list:
            changedList = []
            for item in value:
                if type(item) == dict:
                    changedList.append(normalizeKeys(item))
                else:
                    changedList.append(item)
            changed[changedName] = changedList
        else:
            changed[changedName] = value
    return changed
