import os
import sys
rootpath = os.path.dirname(os.getcwd())
sys.path.append(os.path.join(rootpath, 'radio'))
sys.path.append(os.path.join(rootpath, 'common'))
from Equalizer import Equalizer
from dictToObj import obj, objFromJson, objToJson
import logging

class Sound:
	Filepath = '/var/radio/conf/sound.json'
	def __init__(self):
		self._equalizers = []
		self._selectedEqualizer = ""
		
	def getEqualizers(self):
		if len(self._equalizers) == 0:
			equalizers = Equalizer.GetInstance().getPresets()
			for index, value in enumerate(equalizers):
				item = {'index': index, 'name': value.decode('ascii')}
				self._equalizers.append(item)
		
		return self._equalizers
		
	def getSelectedEqualizer(self):
		if self._selectedEqualizer == "":
			soundConfig = objFromJson(Sound.Filepath)
			self._selectedEqualizer = soundConfig.equalizer.index
			
		return self._selectedEqualizer
		
	def change(self,equalizerIndex):
		try:
			equalizerName = Equalizer.GetInstance().getPresetName(equalizerIndex)
			self.write(equalizerIndex, equalizerName.decode('utf-8'))
		except IndexError:
			login.debug(f"Sound.change(equalizerIndex={equalizerIndex}) index not found")
			
	def write(self, index, name):
		o = obj({'equalizer': {'index': index, 'name': name}})
		jsonString = objToJson(o)
		logging.debug(f"Sound.write(jsonString={jsonString})")
		with open(Sound.Filepath, 'w') as f:
			f.write(jsonString)
			f.close()
		
			
if __name__ == "__main__":
	sound = Sound()
	equalizers = sound.getEqualizers()
	print(equalizers)
	selectedEqualizer = sound.getSelectedEqualizer()
	print(selectedEqualizer)	
