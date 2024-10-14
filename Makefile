DOCKER_IMAGE_NAME=stateful-ml-terminal
POD_NAME=terminal-pod

# Default target, does everything
.PHONY: term
term: docker-build create-pod


.PHONY: docker-build
docker-build:
	eval $$(minikube docker-env) && docker compose build terminal

.PHONY: create-pod
create-pod:
	kubectl run $(POD_NAME) --image=$(DOCKER_IMAGE_NAME):latest --image-pull-policy=Never --rm -i --tty
