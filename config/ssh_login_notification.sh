# PAM hook (/etc/pam.d/sshd)
# session optional pam_exec.so seteuid /home/amy/mine/scripts/ssh_login_notification.sh

#!/bin/sh
if [ "$PAM_TYPE" != "close_session" ]; then
    host="`hostname`"
    curl -d "SSH Login: $PAM_USER from $PAM_RHOST on $host | `env`" localhost:8099/login
fi
