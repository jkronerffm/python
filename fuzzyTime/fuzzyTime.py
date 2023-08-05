import datetime, logging

logger = logging.getLogger("fuzzyTime")
loggingFormat='%(asctime)s %(name)s %(filename)s:%(lineno)d%(funcName)s %(message)s'

def get_fuzzy_time(time):
    hourRule = lambda minute, hour: (12 if minute < 25 else 1) if hour%12 == 0 else ((hour%12) if minute < 25 else ((hour+1)%12) if ((hour%12) < 11) else 12)
    rules = [
        [lambda minute: minute == 0 or minute == 60, lambda minute, hour: hourRule(minute, hour)],
        [lambda minute: minute == 15, lambda minute, hour: "Viertel nach %s" % (hourRule(minute, hour))],
        [lambda minute: minute == 25, lambda minute, hour: "%s vor halb %s" % (5, hourRule(minute, hour))],
        [lambda minute: minute <  25, lambda minute, hour: "%s nach %s" % (minute, hourRule(minute, hour))],
        [lambda minute: minute == 30, lambda minute, hour: "halb %s" % (hourRule(minute, hour))],
        [lambda minute: minute == 35, lambda minute, hour: "%s nach halb %s" % (5,hourRule(minute, hour))],
        [lambda minute: minute == 45, lambda minute, hour: "Viertel vor %s" % (hourRule(minute, hour))],
        [lambda minute: True, lambda minute, hour: "%d vor %s" % ((60-minute),hourRule(minute, hour))]
    ]
    hour = time.hour
    minute = time.minute // 5 * 5 + (5 if (time.minute % 5) > 2 else 0)
    logger.debug("(hour=%s, minute=%s, hourRule=%s)" % (hour, minute, hourRule(minute,  hour)))
    fuzzyTime = ""
    for rule in rules:
        if rule[0](minute):
            fuzzyTime = rule[1](minute, hour)
            break
    return fuzzyTime

if __name__=="__main__":
    logging.basicConfig(level=logging.ERROR, format=loggingFormat)
    for time in [datetime.datetime.now().time(),
                 datetime.time(hour=14, minute=59),
                 datetime.time(hour=0,minute=23),
                 datetime.time(hour=23, minute=37),
                 datetime.time(hour=11, minute=32)]:
        fuzzyTime = get_fuzzy_time(time)
        print("%s -> %s" % (time, fuzzyTime))

