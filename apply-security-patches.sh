#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! hash rpm; then
    echo "rpm missing; are you running on rhel|centos?"
    exit 1
fi

if ! hash yum-wrapper; then
    echo "yum-wrapper missing; are you running as root?"
    exit 1
fi

# cleanup old kernels
/usr/bin/package-cleanup --oldkernels --count=1 -y

# apply security updates
/usr/local/sbin/yum-wrapper upgrade --security -y --skip-broken

CURR_KERNEL=`uname -r`
LAST_KERNEL=`rpm -q --last kernel | head -1 | awk '{print $1}' | sed -r 's/kernel-(.*)/\1/'`

if [ "$CURR_KERNEL" != "$LAST_KERNEL" ]; then

    # optionally communicate downtime here

    # shut down Apache gracefully
    if [ -f /usr/sbin/apachectl ]; then
        /usr/sbin/apachectl -k graceful-stop
    fi

    #trigger a reboot
    /sbin/shutdown -r now "apply-security-patches"
fi
