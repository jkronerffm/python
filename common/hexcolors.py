def hexToRgb(hx):
    return (int(hx[1:3],16), int(hx[3:5],16), int(hx[5:7],16))
    
def rgbTupleToHex(colortuple):
    return "#" + ''.join(f'{i:02X}' for i in colortuple)
    
def rgbToHex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)
    
if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    s = rgbTupleToHex((128,0,0))
    logging.debug(f"color string: {s}")
    t = hexToRgb(s)
    logging.debug(f"color tuple: {t}")
