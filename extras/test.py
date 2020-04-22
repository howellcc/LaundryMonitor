
import datetime

x = 2


def main():
    #experimenting with scope
    global x
    print(x)
    x = 3


    #experimenting with datetimes and time deltas
    startdate = datetime.datetime(2021,4,22,1,0,0)
    startdate = datetime.datetime(9999,1,1,0,0,0)
    enddate = datetime.datetime.now()
    timedelt = enddate - startdate
    print(startdate)
    print(enddate)
    print(timedelt)
    print(timedelt.total_seconds())

    return;

main()
print(x)
x=4
main()
