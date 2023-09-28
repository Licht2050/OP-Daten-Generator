# Json Parser for C++
sudo apt install nlohmann-json3-dev

# Boost library for C++ 
sudo apt-get install libboost-all-dev

# Posix IPC for python
pip install posix_ipc

# for MongodDB
pip install pydantic

# for graphql
install postman client

## to install in ubuntu
download from https://www.postman.com/downloads/
sudo tar -xzf Postman-linux-x64-7.36.1.tar.gz -C /opt
sudo ln -s /opt/Postman/Postman /usr/bin/postman
#### to add Postman to applications menu
echo -e '[Desktop Entry]\n Name=Postman\n Exec=/opt/Postman/Postman\n Icon=/opt/Postman/app/resources/app/assets/icon.png\n Type=Application\n X-GNOME-DocPath=postman:/opt/Postman/Postman\n Categories=Network;WebBrowser;Development;\n Keywords=network;postman;\n' | sudo tee /usr/share/applications/postman.desktop



# install channels in django
pip install -U channels["daphne"]


# aioredis
pip install aioredis

