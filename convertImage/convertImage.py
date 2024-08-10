from PIL import Image
import os

def getNewFilepath(filepath, appendix):
    dirname = os.path.dirname(filepath)
    basename= os.path.basename(filepath)
    filename, ext = os.path.splitext(basename)
    newFilepath = os.path.join(dirname, "%s_%s%s" % (filename, appendix, ext))
    return newFilepath

def convertImage(filepath, bgColor : tuple, outFilePath):
    img = Image.open(filepath)
    img = img.convert("RGBA")

    datas = img.getdata()

    newData = []

    for item in datas:
        if item[0] == bgColor[0] and item[1] == bgColor[1] and item[2] == bgColor[2]:
            newData.append((bgColor[0], bgColor[1], bgColor[2], 0))
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(outfilepath)

if __name__ == "__main__":
    filepath = "/var/radio/pics/hr3.png"
    outfilepath = getNewFilepath(filepath, "new")
    print("input: %s\noutput: %s" % (filepath, outfilepath))
    convertImage(filepath, (255,255,255), outfilepath)
    
