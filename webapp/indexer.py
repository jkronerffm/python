import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
from common import dictToObj
import uuid

filepath = "/var/radio/conf/radio.json"
data = dictToObj.objFromJson(filepath)
for sender in data.sender:
    if not (hasattr(sender, "id")):
        id = str(uuid.uuid4())
        setattr(sender, "id", id)

jsonStr = dictToObj.objToJson(data)
with open(filepath, "w") as f:
    f.write(jsonStr)
