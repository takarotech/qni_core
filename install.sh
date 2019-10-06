#!/bin/bash

#-> Make sure we don't run as root
if (( EUID == 0 )); then
   echo 'Please run without sudo!' 1>&2
   exit 1
fi

#-> Go to the directory of this script
cd "$(dirname "${BASH_SOURCE[0]}")"

#-> Install tkinter and numpy from apt (pip seems to fail..)
sudo apt install -y python3-tk python3-numpy

#-> Install qni_core package
sudo -H ./setup.py install

#-> Exit here if needed
QNI_CONF_FILE_PATH=$HOME/qni_conf.json
if [ -f $QNI_CONF_FILE_PATH ]; then
    echo 'Found qni_conf file, skipping full installation!'
	exit 0
fi

#-> Copy the default qni configuration to the user dir
cp res/qni_default_conf.json $QNI_CONF_FILE_PATH

#-> Create 'uinput' group and add 'pi' user to both 'input' groups
CUR_USER=$(whoami)
sudo groupadd -f uinput
sudo gpasswd -a $CUR_USER input
sudo gpasswd -a $CUR_USER uinput

#-> Create udev rule that changes input devices permissions
sudo sh -c 'cat > /etc/udev/rules.d/99-uinput.rules <<EOF
KERNEL=="uinput", MODE="0660", GROUP="uinput", OPTIONS+="static_node=uinput"
KERNEL=="event*", MODE="0660", GROUP="input", NAME="input/%k"
EOF'
sudo udevadm control --reload-rules
sudo udevadm trigger
