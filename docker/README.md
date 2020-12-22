To create a new docker image, and release it to Github (NOT Docker Central):

1. Get your Personal Access Token from Github (under your personal Settings > Developer settings)
2. Use that to do a `docker login ghcr.io -u USERNAME`
3. Update the `Dockerfile` to the correct thriftcli version
4. Build a docker image by doing `docker image build docker`
5. Do a `docker image ls` and note the image id
6. Tag your Docker image by doing `docker image tag IMAGEID ghcr.io/fitbit/thriftcli:VERSION`
7. Push your image by doing `docker push ghcr.io/fitbit/thriftcli:VERSION`
