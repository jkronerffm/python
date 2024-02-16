import vlc
import time

class Equalizer:
    Instance = None
    
    def __init__(self):
        self._frequencies = None
        self._presets = None

    @staticmethod
    def GetInstance():
        if Equalizer.Instance == None:
            Equalizer.Instance = Equalizer()
        return Equalizer.Instance
    
    def getBandCount(self):
        frequencies = self.getFrequencies()
        return len(frequencies)
            
    def getFrequencies(self):
        if self._frequencies == None:
            self._frequencies = []
            bandCount = vlc.libvlc_audio_equalizer_get_band_count()
            for bandIndex in range(bandCount):
                frq = vlc.libvlc_audio_equalizer_get_band_frequency(bandIndex)
                self._frequencies.append(frq)

        return self._frequencies

    def getFrequencyAtBand(self,bandIndex):
        frequencies = self.getFrequencies()
        if bandIndex < 0 or bandIndex >= Equalizer.GetBandCount():
            raise IndexError()
        return frequencies[bandIndex]
        
    def getFrequencyBand(self, frequency):
        if self.hasFrequency(frequency):
            frequencies = self.getFrequencies()
            return frequencies.index(frequency)
        else:
            raise IndexError()

    def hasFrequency(self,frequency):
        frequencies = self.getFrequencies()
        return frequency in frequencies
            
    def getPresetCount(self):
        presets = self.getPresets()
        presetCount = len(presets)
        return presetCount

    def getPresets(self):
        presets = []
        presetCount = vlc.libvlc_audio_equalizer_get_preset_count()
        for index in range(presetCount):
            presetName = vlc.libvlc_audio_equalizer_get_preset_name(index)
            presets.append(presetName)
        return presets

    def getPresetIndex(self, presetName):
        if self.hasPresetName(presetName):
            presets = self.getPresets()
            return presets.index(presetName)
        else:
            raise IndexError()

    def getPresetName(self, index):
        if index < 0 or index >= self.getPresetCount():
            raise IndexError()
        presets = self.getPresets()
        presetName = presets[index]
        return presetName

    def getEqualizerByIndex(self,index):
        if index < 0 or index >= self.getPresetCount():
            raise IndexError()
        equalizer = vlc.libvlc_audio_equalizer_new_from_preset(index)
        return equalizer

    def getEqualizerByName(self, presetName):
        try:
            index = self.getPresetIndex(presetName)
            return self.getEqualizerByIndex(index)
        except IndexError:
            logging.error("IndexError in Equalizer.getEqualizerByName")
            return None

    def hasPresetName(self, presetName):
        presets = self.getPresets()
        return presetName in presets

if __name__ == "__main__":
    instance =vlc.Instance()
    player = instance.media_list_player_new()
    mediaPlayer = player.get_media_player()
    mediaList = instance.media_list_new()
    media = instance.media_new("http://metafiles.gl-systemhaus.de/hr/hr1_2.m3u")
    mediaList.add_media(media)
    player.set_media_list(mediaList)
    player.play()
    mediaPlayer.audio_set_volume(50)
    equalizerInstance = Equalizer.GetInstance()

    print("Bands...")
    frequencies = equalizerInstance.getFrequencies()
    for frq in frequencies:
        print(f"  Band {equalizerInstance.getFrequencyBand(frq)} -> {str(frq)}.1Hz")

    print("Presets...")
    presets = equalizerInstance.getPresets()
    for i in range(len(presets)):
        print(f"  Preset {i} -> {presets[i]}")

    preset = 0  
    while True:
        name = equalizerInstance.getPresetName(preset)
        equalizer = equalizerInstance.getEqualizerByIndex(preset)
        print(f"  try equalizer preset {name}")
        mediaPlayer.set_equalizer(equalizer)
        preset+= 1
        if preset >= equalizerInstance.getPresetCount():
            preset = 0
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            break

    print("stop player")
    player.stop()

