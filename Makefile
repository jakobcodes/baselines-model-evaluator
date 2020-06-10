VERSION="2020-06-10"
docker:
	docker build -t pkoperek/baselinesme:latest -t pkoperek/baselinesme:${VERSION} .

docker-push: docker
	docker push pkoperek/baselinesme:${VERSION}
	docker push pkoperek/baselinesme:latest
