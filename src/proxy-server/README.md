docker build -t proxy-server .
docker run -p 3001:3001 -it --rm proxy-server