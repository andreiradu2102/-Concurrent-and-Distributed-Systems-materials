docker build -t scd_web:latest .

docker swarm init

docker stack deploy -c new_stack.yml scd
