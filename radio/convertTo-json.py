import xmltodict
from pathlib import Path
import json, os
import logging
from normalizeKeys import normalizeKeys

logging.basicConfig(level=logging.DEBUG)
path = "waketime.xml"
basename = Path(path).stem
content = xmltodict.parse(Path(path).read_text())
print("content from file \"%s\": %s" % (path, content))
changedContent = normalizeKeys(content)
print(str(changedContent))
jsonfile = "%s.%s" % (basename, "json")
with open(jsonfile, 'w') as f:
    json.dump(changedContent, f, indent=2)

with open(jsonfile) as f:
    content = json.load(f)
    print("content from \"%s\": %s" % (jsonfile, content))

                        
