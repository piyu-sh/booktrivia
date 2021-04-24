docker build -t proxy-server .
docker run -p 3001:3001 -it --rm proxy-server

// TODO maybe if needed try injecting `resolver.py`in serverless like its done in dockerfile