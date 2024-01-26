import subprocess
import logging

def get_dev(label):
    logging.debug(f"get_dev(label=\"{label}\")")
    proc = subprocess.Popen([f"blkid --label {label}"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    dev = out.decode("ascii").strip()
    logging.debug(f">> returns dev=\"{dev}\"")
    return dev
    
def get_uuid(label="rootfs"):
    logging.debug(f"get_uuid(label=\"{label}\")")
    dev = get_dev(label)
    proc = subprocess.Popen([f"blkid {dev} -s UUID | cut -d'=' -f2 | tr -d '\"'"], stdout = subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    uuid = out.decode("ascii").strip()
    logging.debug(f">> returns uuid=\"{uuid}\"")
    return uuid

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    uuid = get_uuid()
    print(f"computer's uuid: {uuid}")
    
    
