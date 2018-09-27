#!/bin/bash
#http://alex.nisnevich.com/blog/2014/10/01/setting_up_flask_on_ec2.html

sudo apt-get update
sudo apt-get install apache2 apache2-mpm-prefork apache2-utils libexpat1 ssl-cert
sudo apt-get install libapache2-mod-wsgi python-pip git


mkdir -p /srv/src
cd /srv/src
sudo git clone https://github.com/startach/dMelechServer.git
sudo pip install -r dMelechServer/scripts/requirements.txt

sudo cp /srv/src/dMelechServer/apache_conf/jworld.startach.org.il.conf /etc/apache2/sites-available
sudo a2ensite jworld.startach.org.il
sudo a2dissite 000-default  # and for good measure, let's disable the default placeholder site


sudo service apache2 restart
#sudo apachectl restart
