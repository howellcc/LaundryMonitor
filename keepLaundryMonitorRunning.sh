#! /bin/bash

#this can be put into a crontab with the following
# * * * * * /{insert path here}/keepLaundryMonitorRunning.sh >/dev/null 2>&1

case "$(pidof python3 laundrymonitor.py | wc -w)" in

0)  echo "Restarting Laundry Monitor:     $(date)" >> /home/chowell/laundry.txt
	cd /home/chowell/LaundryMonitor
	python3 laundrymonitor.py &
	;;
1)  # There is exactly 1 instance running. Nothing to do.
	;;
*)  # There is more than 1 instance running. Kill the last one.
	echo "Removed double LaundryMonitor: $(date)" >> /home/chowell/laundry.txt
	kill $(pidof python3 laundrymonitor.py | awk '{print $1}')
    ;;
esac
