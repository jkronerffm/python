from os import listdir
from os.path import join, isfile
from urllib.parse import unquote, urlparse
import logging
import random

def shufflePlayList(url):
    path = unquote(urlparse(url).path)
    logging.debug(f"shufflelPlayList(url={url}, path={path})")
    if path.endswith('.m3u'):
        with open(path, 'r') as f:
            files = [filename.strip() for filename in f.readlines()]
            f.close()
    else:
        files = [join(path,f) for f in listdir(path) if isfile(join(path, f))]
    random.shuffle(files)
    return files

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    files = shufflePlayList("file:///var/radio/music")
    print(files)
