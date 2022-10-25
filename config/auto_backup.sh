#!/bin/bash
if [ ! -d "/mnt/backup/tue_backup" ]; then
        echo "Backup folder not mounted"
        exit 1
fi

rclone sync /media/anne/bottle/ /mnt/backup/tue_backup/.live/ --log-level INFO --log-file /home/anne/mine/scripts/backup_bottle.log
