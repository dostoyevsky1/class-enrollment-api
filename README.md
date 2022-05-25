# class-enrollment-api
A simple API for a university class enrollment system

## Quickstart
run ```docker-compose up --build``` from within cloned repo dir

the api will be available on localhost:8000 with docs on localhost:8000/docs

the database will populate with toy data that can be tested out with postman or with manual API requests (from within docs as well)
postman collection included in repo: ```class-enrollment.postman_collection.json```

data in database is persisted locally therefore in order to successfully startup the api after the container was shut down you should run
```rm -rf ~/pgdata```
