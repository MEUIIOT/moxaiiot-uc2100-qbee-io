apt-get update
xargs -a /home/moxa/application/install/apt_packages.txt apt-get install -y
sudo -u moxa pip3 install --user -r /home/moxa/application/install/requirements.txt