#!/bin/bash

BOT_SCRIPT="bot.py"
LOG_FILE="bot.log"
CONDA_ENV="arcteryx"

start_bot() {
    if [ -f "$LOG_FILE" ]; then
        echo "Bot is already running. Check the log file: $LOG_FILE"
    else
        source activate $CONDA_ENV || { echo "Failed to activate Conda environment. Make sure Conda is installed and initialized."; exit 1; }
        nohup python3 $BOT_SCRIPT > $LOG_FILE 2>&1 &
        echo "Bot started. Log file: $LOG_FILE"
    fi
}

stop_bot() {
    if [ -f "$LOG_FILE" ]; then
        pkill -f "$BOT_SCRIPT"
        rm $LOG_FILE
        echo "Bot stopped."
    else
        echo "Bot is not running."
    fi
}

case "$1" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        stop_bot
        start_bot
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac

exit 0
