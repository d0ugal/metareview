#!/bin/bash

set -e;
set -x;


sudo add-apt-repository ppa:webupd8team/java;
sudo apt-get update -y;
sudo apt-get autoremove -y;
sudo apt-get install oracle-java7-installer -y;

pushd /tmp/;
wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.4.3.deb;
sudo dpkg -i elasticsearch-1.4.3.deb;
popd;

sudo apt-get install python-dev python-pip -y;
sudo apt-get build-dep python-numpy -y;
sudo pip install virtualenvwrapper;
echo "
source /usr/local/bin/virtualenvwrapper.sh" >> "$(echo /home/vagrant/.bashrc)";

sudo service elasticsearch start;
sudo /usr/share/elasticsearch/bin/plugin -i elasticsearch/marvel/latest;
sudo /usr/share/elasticsearch/bin/plugin -i mobz/elasticsearch-head;
