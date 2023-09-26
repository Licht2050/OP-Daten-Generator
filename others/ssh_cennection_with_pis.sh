#!/bin/bash


SERVER_IP="192.168.29.120"
SERVER_USER="sayed.sajadi"

for i in {1..5}:
do
    gnome-terminal --tab -- bash -c "ssh $SERVER_USER@$SERVER_IP; bash"
done



# Dieses Skript startet eine SSH-Verbindung zu allen Raspberry Pis in einem neuen Tab.

# Eine Liste von Raspberry Pi IP-Adressen
PI_HOSTS=("192.168.201.251" "192.168.201.250" "192.168.201.229" "192.168.201.167")

Starte SSH-Verbindung für jeden Host in einem neuen Tab
for HOST in "${PI_HOSTS[@]}"; do
    gnome-terminal --tab -- bash -c "ssh pi@$HOST; bash"
done


