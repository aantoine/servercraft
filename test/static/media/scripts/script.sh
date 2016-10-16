#!/bin/bash

# version 0.4.0 2015-04-20 (YYYY-MM-DD)
#
### BEGIN INIT INFO
# Required-Start: $local_fs $remote_fs screen-cleanup
# Required-Stop:  $local_fs $remote_fs
# Should-Start:   $network
# Should-Stop:    $network
# Default-Start:  2 3 4 5
# Default-Stop:   0 1 6
# Short-Description:    Minecraft server
# Description:    Starts the minecraft server
### END INIT INFO

#Settings
SERVICENAME='minecraft_'
LOGS='/logs'

ME=`whoami`
as_user() {
  if [ "$ME" = "$USERNAME" ] ; then
    bash -c "$1"
  else
    bash -c "$1"
  fi
}
 
mc_start() {
  # $1 = server path
  # $2 = server name
  # $3 = jar path
  # $4 = jar xmx
  # $5 = jar xms
  # $6 = sleep time
  local SERVICE=$SERVICENAME$2
  local INVOCATION="java -Xmx$4M -Xms$5M -jar $3 nogui"
  if  pgrep -f $SERVICE > /dev/null
  then
    echo "warning"
  else
    as_user "cd $1 && screen -dmS ${SERVICE} $INVOCATION"
    sleep $6
    if pgrep -f $SERVICE > /dev/null
    then
      echo "success"
    else
      echo "error"
    fi
  fi
}

mc_stop() {
  # $1 = server name
  local SERVICE=$SERVICENAME$1
  if pgrep -f $SERVICE > /dev/null
  then
    as_user "screen -S ${SERVICE} -X eval 'stuff \"say SERVER SHUTTING DOWN IN 10 SECONDS. Saving map...\"\015'"
    as_user "screen -S ${SERVICE} -X eval 'stuff \"save-all\"\015'"
    sleep 10
    as_user "screen -S ${SERVICE} -X eval 'stuff \"stop\"\015'"
    sleep 5

     if pgrep -f $SERVICE > /dev/null
     then
       echo "error"
     else
       echo "success"
     fi

  else
    echo "warning"
  fi
} 

mc_command() {
  command="$1";
  if pgrep -f $SERVICE > /dev/null
  then
    pre_log_len=`wc -l "$MCPATH/logs/latest.log" | awk '{print $1}'`
    echo "$SERVICE is running... executing command"
    as_user "screen -S ${SCREENNAME} -X eval 'stuff \"$command\"\015'"
    sleep .1 # assumes that the command will run and print to the log file in less than .1 seconds
    # print output
    # tail -n $[`wc -l "$MCPATH/logs/latest.log" | awk '{print $1}'`-$pre_log_len] "$MCPATH/logs/latest.log"
  fi
}

mc_log() {
  # $1 = server path
  local LOGPATH=$1$LOGS
  as_user "cd $LOGPATH && cat latest.log"
}

#Start-Stop here
case "$1" in
  start)
    mc_start $2 $3 $4 $5 $6 $7
    ;;
  stop)
    mc_stop $2
    ;;
  restart)
    mc_stop $2
    mc_start $2 $3 $4 $5 $6
    ;;
  log)
    mc_log
    ;;
  status)
    if pgrep -f $SERVICENAME$2 > /dev/null
    then
      echo "$2 online"
    else
      echo "$2 offline"
    fi
    ;;
  command)
    if [ $# -gt 1 ]; then
      shift
      mc_command "$*"
    else
      echo "Must specify server command (try 'help'?)"
    fi
    ;;

  *)
  echo "Usage: $0 {start|stop|backup|status|data|restart|command \"server command\"}"
  exit 1
  ;;
esac

exit 0
