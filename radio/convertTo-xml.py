import xmltodict
from pathlib import Path
import json, os

path = "waketime.xml"
basename = Path(path).stem
content = xmltodict.parse(Path(path).read_text())
with open('%s.json' % basename, 'w') as f:
    json.dump(content, f)

                        
