#!/bin/bash
sleep 15
mount -t cifs -o username=amy,password=a1s2d3,dir_mode=0777,file_mode=0777 //192.168.2.1/backup/ /mnt/backup
mount -t cifs -o username=amy,password=a1s2d3,dir_mode=0777,file_mode=0777 //192.168.2.1/media/ /mnt/media
