build:
	eval $(minikube -p minikube docker-env) && docker build -t droit-local:1.0.0 .

deploy-mongo:
	kubectl apply -f deployments/mongo-secret.yaml
	kubectl apply -f deployments/mongo-configmap.yaml
	kubectl apply -f deployments/mongo.yaml

deploy: build deploy-mongo
	eval $(minikube -p minikube docker-env) && \
	kubectl apply -f deployments/droit.yaml

# install:

# minikube addons enable ingress