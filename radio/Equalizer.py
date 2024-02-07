import vlc
import time

instance =vlc.Instance()
player = instance.media_list_player_new()
mediaPlayer = player.get_media_player()
mediaList = instance.media_list_new()
media = instance.media_new("http://metafiles.gl-systemhaus.de/hr/hr1_2.m3u")
mediaList.add_media(media)
player.set_media_list(mediaList)
player.play()
mediaPlayer.audio_set_volume(50)
print("Bands...")
u_bands = vlc.libvlc_audio_equalizer_get_band_count()
for i in range(u_bands):
    frq = vlc.libvlc_audio_equalizer_get_band_frequency(i)
    print(f"  Band {i} -> {str(frq)}.1Hz")

print("Presets...")
u_presets = vlc.libvlc_audio_equalizer_get_preset_count()
for i in range(u_presets):
    preset = vlc.libvlc_audio_equalizer_get_preset_name(i)
    print(f"  Preset {i} -> {preset}")

preset = 0  
while True:
    name = vlc.libvlc_audio_equalizer_get_preset_name(preset)
    equalizer = vlc.libvlc_audio_equalizer_new_from_preset(preset)
    print(f"  try equalizer preset {name}")
    mediaPlayer.set_equalizer(equalizer)
    preset+= 1
    if preset >= u_presets:
        preset = 0
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        break

print("stop player")
player.stop()
