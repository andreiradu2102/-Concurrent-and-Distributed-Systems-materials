docker build -t task1 .
docker run --name task1_c -p 8080:80 -d task1
