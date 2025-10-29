docker build -t scd_web:latest .

docker swarm init

docker stack deploy -c stack.yml scd
