set -ex
# SET THE FOLLOWING VARIABLES
# docker hub username
USERNAME=
# image name
IMAGE=
docker build -t $USERNAME/$IMAGE:latest .