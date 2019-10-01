#!/bin/bash
cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
HOME_DIR=$(pwd | cut -d/ -f 1-3)
USER_NAME=$(pwd | cut -d/ -f 3-3)
sudo apt install -y python3 python3-pip python3-tk python3-numpy
sudo -H ./setup.py install
sudo -u $USER_NAME cp res/qni_default_conf.json $HOME_DIR/qni_conf.json

sudo groupadd -f uinput
sudo gpasswd -a $USER_NAME input
sudo gpasswd -a $USER_NAME uinput
# change /dev/uinput permissions
sudo sh -c 'cat > /etc/udev/rules.d/99-uinput.rules <<EOF
KERNEL=="uinput", MODE="0660", GROUP="uinput", OPTIONS+="static_node=uinput"
KERNEL=="event*", MODE="0660", GROUP="input", NAME="input/%k"
EOF'
sudo udevadm control --reload-rules
sudo udevadm trigger
