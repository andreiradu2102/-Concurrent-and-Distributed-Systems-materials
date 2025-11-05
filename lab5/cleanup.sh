docker stop $(docker ps -aq) 2>/dev/null
docker rm $(docker ps -aq) 2>/dev/null

docker rmi -f $(docker images -aq) 2>/dev/null

docker volume rm $(docker volume ls -q) 2>/dev/null

docker network rm $(docker network ls -q) 2>/dev/null

docker system prune -a --volumes
