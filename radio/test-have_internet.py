import sys
sys.path.append("/home/jkroner/Documents/python/have_internet")
import  have_internet
from have_internet import haveInternet

print("internet %s available %s" % ("is", ":)") if haveInternet() else ("is not", ":("))
    
