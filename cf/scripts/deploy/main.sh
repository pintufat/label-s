#!/usr/bin/env bash

# This script runs a full deployment of SalmonVision
# It requires that the STAGE variable is set to either prod or dev
# It does the following:
# - Deploy the cloudformation infrastructure
# - Logging into ECR
# - Build and push a docker image of the local code to the ECR repository
# - Trigger an elastic beanstalk environment deploy

set -x

project_root="$(dirname "${BASH_SOURCE[0]}")/../../.."

"${project_root}"/cf/scripts/utils/check_stage.sh

# Check the exit status of the external script
if [[ $? -ne 0 ]]; then
	echo "Exiting main script due to error in check_stage.sh"
	exit 1
fi

DOCKER_CONTAINER_REPOSITORY=391155498039.dkr.ecr.eu-north-1.amazonaws.com
DOCKER_IMAGE_NAME="${DOCKER_CONTAINER_REPOSITORY}/${STAGE}-salmonvision-webapp"
GIT_SHA=$(git rev-parse --short HEAD)

echo "Deploying AWS infrastructure"
"${project_root}"/cf/scripts/deploy/infra/main.sh

echo "Building docker image"
docker build \
	-t "${DOCKER_IMAGE_NAME}:${GIT_SHA}" \
	-t "${DOCKER_IMAGE_NAME}:latest" \
	"${project_root}"

echo "Logging into ECR"
aws ecr get-login-password | docker login --username AWS --password-stdin ${DOCKER_CONTAINER_REPOSITORY}

echo "Pushing to ECR"
docker push "${DOCKER_IMAGE_NAME}:${GIT_SHA}"
docker push "${DOCKER_IMAGE_NAME}:latest"

echo "Deploying new environment code"
"${project_root}"/cf/scripts/deploy/environment/main.sh