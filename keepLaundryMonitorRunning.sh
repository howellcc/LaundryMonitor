#! /bin/bash

case "$(pidof python3 laundrymonitor.py | wc -w)" in

0)  echo "Restarting Laundry Monitor:     $(date)" >> /home/chowell/laundry.txt
	cd /home/chowell/LaundryMonitor
	python3 laundrymonitor.py &
    ;;
1)  # all ok
    ;;
*)  echo "Removed double LaundryMonitor: $(date)" >> /home/chowell/laundry.txt
    kill $(pidof python3 laundrymonitor.py | awk '{print $1}')
    ;;
esac
