APP_NAME=terminal
DEPLOYMENT_NAME=terminal-deployment

.PHONY: term
term: docker-build scale-up attach-pod scale-down

.PHONY: docker-build
docker-build:
	eval $$(minikube docker-env) && docker compose build terminal

.PHONY: scale-up
scale-up:
	kubectl scale deployment $(DEPLOYMENT_NAME) --replicas=1

.PHONY: attach-pod
attach-pod:
	# Wait for the new pod to be running, then attach
	kubectl wait --for=condition=Ready pod -l app=$(APP_NAME) --timeout=120s
	kubectl attach -it $$(kubectl get pod -l app=$(APP_NAME) -o jsonpath="{.items[0].metadata.name}")

.PHONY: scale-down
scale-down:
	kubectl scale deployment $(DEPLOYMENT_NAME) --replicas=0
