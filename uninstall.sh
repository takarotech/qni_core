#!/bin/bash

#-> Make sure we don't run as root
if (( EUID == 0 )); then
   echo 'Please run without sudo!' 1>&2
   exit 1
fi

#-> Uninstall this package (pip uses '-' instead of '_')
pip3 uninstall qni-core -y
