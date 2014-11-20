#!/bin/sh

#This is a script to check if agentcodes.py is running on the server, if it isn't it will restart it.
#You cant schedule a cron job like this:
# */5 * * * * /path/to/script/agentmonitor.sh

#Uncomment to activate logs  
exec 1>>/home/grtd/grtd/agentmonitor.log

#Uncomment the following two lines to active the debug mode (in case the script is not working as expected)
#exec 2>>/home/grtd/grtd/agentmonitor.err
#set -x

ps -Ao args | grep python | grep -q agentcodes.py
case $? in
(0)
echo $(date) agentcodes OK
;;
(*)
echo $(date) agentcodes NOK
/home/grtd/grtd/agentcodes.py &
;;
esac
