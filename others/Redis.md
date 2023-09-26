# install redis on ubuntu
sudo apt-get install redis-server

# configure redis
sudo vim /etc/redis/redis.conf
change supervised no to supervised systemd

# restart redis
sudo systemctl restart redis-server

# enable redis
sudo systemctl enable redis-server

# check redis status
sudo systemctl status redis-server

# check redis version
redis-server -v

# test redis installation
redis-cli

redis-server is running in = 127.0.0.1:6379

# start redis
redis-server