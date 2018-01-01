#!/bin/bash

export MY_PUBIP="`curl -s ipinfo.io/ip`"
export COUNTRY_CODE="`curl -s ipinfo.io/${MY_PUBIP} | grep country | sed 's%^.*: "\(..\)",.*$%\1%g' | tr '[:upper:]' '[:lower:]'`"
echo ${MY_PUBIP} ${COUNTRY_CODE}

TEMP="`ip addr | grep 'inet ' | grep -v '127.0.0.1' | head -1 | xargs echo -n`"
export MY_IP="`echo -n ${TEMP} | cut -d ' ' -f 2 | cut -d '/' -f 1`"
export MY_BCAST="`echo -n ${TEMP} | cut -d ' ' -f 4`"

apt -y install gettext socat

# NTPD

# GPS PPS on GPIO pin
grep "^dtoverlay=pps-gpio,gpiopin=4$" /boot/config.txt >/dev/null || echo "dtoverlay=pps-gpio,gpiopin=4" >> /boot/config.txt >/dev/null

# deploy NTPD configuration with enable PPS and country based pool servers
cat files/ntp.conf | envsubst > /etc/ntp.conf

# deploy rtklib configuration files
cp -arv files/rtklib /etc/

