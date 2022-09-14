set -ex
# SET THE FOLLOWING VARIABLES
# docker hub username
USERNAME=
# image name
IMAGE=
# ensure we're up to date
# git pull
# bump version
#CHECK OUT FOR DOCUMENTATION
#docker run --rm -v "$PWD":/app treeder/bump patch
#version=`cat VERSION`
VERSION=`(git tag --sort=-v:refname --list "v[0-9]*" | head -n 1 | cut -c 2-)`
echo "version: $VERSION"

# run build
./build.sh
# tag it
# git add -A
# git commit -m "version $version"
# git tag -a "$version" -m "version $version"
# git push
# git push --tags
# login command with iam role
#aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $USERNAME

#tag command
docker tag $USERNAME/$IMAGE:latest $USERNAME/$IMAGE:$VERSION
# push it
docker push $USERNAME/$IMAGE:latest
docker push $USERNAME/$IMAGE:$VERSION