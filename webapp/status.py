import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.getcwd()),"ipc"))
from ipc import StatusClient

class Status:
    Data = None
    
    def __init__(self):
        pass

    @staticmethod    
    def ClientCallback(data):
        Status.Data = data
        
    def get(self):
        client = StatusClient(Status.ClientCallback)
        client.run()
        return Status.Data

if __name__ == "__main__":
    status = Status()
    print(status.get())
