docker build -t andreiradu2003/scd6:latest .

docker login

docker push andreiradu2003/scd6:latest

docker swarm init

docker stack deploy -c final_stack.yml scd
