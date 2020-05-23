docker:
	docker build -t pkoperek/baselinseme:latest .

docker-push: docker
	docker push pkoperek/baselinesme:latest
