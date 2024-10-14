APP_NAME=terminal

.PHONY: term
term: docker-build restart-pod attach-pod

.PHONY: docker-build
docker-build:
	eval $$(minikube docker-env) && docker compose build terminal

.PHONY: restart-pod
restart-pod:
	# Delete the current Pod to force Kubernetes to recreate it
	kubectl delete pod -l app=$(APP_NAME) --grace-period=0

.PHONY: attach-pod
attach-pod:
	# Wait for the new pod to be running, then attach
	kubectl wait --for=condition=Ready pod -l app=$(APP_NAME) --timeout=120s
	kubectl attach -it $$(kubectl get pod -l app=$(APP_NAME) -o jsonpath="{.items[0].metadata.name}")
