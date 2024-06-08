#!/bin/bash
docker compose down
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker volume prune -a -f
docker system prune -a -f
docker system images -a -f
cd
rm -rf copr
git clone --branch perso https://github.com/andykimpe/copr.git
cd copr
docker compose up -d
