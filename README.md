# OpenAI Baselines Policy Evaluator

This is a package which is intended to be used with policies generated with
use of [Baselines project from Open AI](https://github.com/openai/baselines).

## Development

Running development server:

`FLASK_APP=baselinesme/api.py flask run -p 8080`

## Running a test query

`curl -X POST -H "Content-Type: application/json" --data @test.rq http://localhost:8080/oracle `

## Running a test deployment and testing it

```
docker-compose up
curl -X POST -H "Content-Type: application/json" --data @test.rq http://localhost:8888/oracle 
```
