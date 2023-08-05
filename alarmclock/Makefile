files = \
      AlarmClockBase.py \
      AlarmTimeBase.py \
      AlarmOneTimeBase.py  \
      AlarmRepeatBase.py

.SUFFIXES:
.SUFFIXES: .py .ui

%.py: %.ui
	pyuic5 $< -o $@

all: $(files)


