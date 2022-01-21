#!/bin/sh
pip install pyelftools --upgrade
pip install dolreader --upgrade
pip install geckolibs --upgrade
sudo python setup.py install
read -rsn1 -p"Press any key to continue . . .";echo;echo
