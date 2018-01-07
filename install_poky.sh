#!/bin/sh

pushd . >/dev/null
cd

opkg update

opkg install curl
curl -L https://api.github.com/repos/navdata-net/installer/tarball/master >installer.tgz
tar -xzf installer.tgz
mv navdata-net-installer-* installer

opkg install parted
opkg install e2fsprogs-resize2fs

parted -s /dev/mmcblk0 resizepart 2 100%
resize2fs /dev/mmcblk0p2 

opkg install ntp
opkg install rtklibexplorer
opkg install pylongps
opkg install nginx

rm /var/www/localhost/html/index.html
cp -ar installer/webroot/* /var/www/localhost/html/

popd

