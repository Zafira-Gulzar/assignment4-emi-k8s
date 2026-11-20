# Loan EMI Calculator on Kubernetes (Assignment 4)

## Prerequisites
- Minikube installed and running (Docker driver)
- kubectl installed
- Docker installed

## How to bring up the system on a fresh Minikube cluster

1. Start Minikube:
   `minikube start --memory=3072mb`

2. Enable Ingress:
   `minikube addons enable ingress`

3. Build and load the application image:
   `cd app`
   `docker build -t emi-web:1.0 .`
   `minikube image load emi-web:1.0`
   `cd ..`

4. Apply all Kubernetes manifests:
   `kubectl apply -f k8s/`

5. Wait for all pods to be running:
   `kubectl get pods -n emi -w`

6. To access the app on Windows/macOS:
   - Add `127.0.0.1 emi.local` to your hosts file.
   - Run `minikube tunnel` in a separate terminal.
   - Open `http://emi.local` in your browser.
