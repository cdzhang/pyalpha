# download and install docker
# https://hub.docker.com/editions/community/docker-ce-desktop-mac/

# install mysql client server
# https://dev.mysql.com/downloads/file/?id=497036
#if you have already installed MySQL from the disk image (dmg) from http://dev.mysql.com/downloads/), open a terminal, run:
echo 'export PATH=/usr/local/mysql/bin:$PATH' >> ~/.bash_profile

#then, reload .bash_profile by running following command:
. ~/.bash_profile

#You can now use mysql to connect to any mysql server:
mysql -h xxx.xxx.xxx.xxx -u username -p



# compose mysql
docker run --name alphadb -p 8084:3306 -e MYSQL_ROOT_PASSWORD=maoxiaomi123 -d mysql:latest

# check images
docker images

# check container
docker ps


docker exec -it alphadb bash

# access to mysql db in my host machine
mysql -P 8084 --protocol=tcp -uroot -pmaoxiaomi123

show databases;
use database_name;
show tables;




------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------


-- create database
CREATE DATABASE alpha;


--,ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount
--`id` INT UNSIGNED AUTO_INCREMENT,
drop table if exists `daily`;
CREATE TABLE IF NOT EXISTS `daily`(
   `ts_code` VARCHAR(40) NOT NULL,
   `trade_date` DATE,
   `open` DOUBLE,
   `high` DOUBLE,
   `low` DOUBLE,
   `close` DOUBLE,
   `pre_close` DOUBLE,
   `change` DOUBLE,
   `pct_chg` DOUBLE,
   `vol` DOUBLE,
   `amount` DOUBLE,
   PRIMARY KEY ( `ts_code`, `trade_date`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8
AUTO_INCREMENT=1;








