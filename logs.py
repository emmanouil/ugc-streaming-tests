import datetime
LOGFILE = 'python_script.log'
DIR = "D:\\Gits\\ugc-streaming-tests\\"

##	Log
#
#	lvl = None log to console
#		< 0 ERROR
#		> 0 INFO
#		= 0 Debug
def log(msg, lvl):
    now = datetime.datetime.now()
    str_now = '\n' + str(now.day) + '/' + str(now.month) + '/' + str(now.year) + ' ' + str(now.hour) + ':' + str(now.minute) + ':' + str(
        now.second) + ' '
    str_now = str_now.ljust(19)
    with open(DIR + LOGFILE, 'a') as logfile:
        if (lvl is None):    #normal
            print(msg)
        elif (lvl < 0):    #error
            print('\033[31;1m' + '[ERROR]\t' + '\033[0m' + msg)
            logfile.write(str_now + '[ERROR]\t' + msg)
        elif (lvl > 0):    #info
            print('\033[32m' + '[INFO]\t' + '\033[0m' + msg)
            logfile.write(str_now + '[INFO]\t' + msg)
        elif (lvl == 0):    #dbg
            print('\033[35;1m' + '[DEBUG]\t' + '\033[0m' + msg)
            logfile.write(str_now + '[DEBUG]\t' + msg)