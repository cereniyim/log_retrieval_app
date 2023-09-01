# Log Retrieval Flask App

This app gets logs for a
- user_id
- date in YYYY-MM-DD format
- log_level
- keyword (optional)

to enable easier debugging of Machine Learning model logs.

It uses MongoDB as hot storage and AWS S3 as cold storage for efficient storing of the logs.

Currently only local deployment of the app is supported.

## Why AWS S3 is selected as cold storage?
I explored several options like MongoDB Datalake, which looks like a native solution to serve as a cold storage for MongoDB.

However, MongoDB Datalake is only supported when MongoDB is deployed to Atlas Clusters. Our use case indicates running 
MongoDB on on-premise clusters, so I selected custom scripting option and AWS S3 as the cold storage solution. 

Please see more details 
[here](https://www.mongodb.com/community/forums/t/connection-between-an-on-premise-cluster-and-a-data-lake/155925).


## Project Organization

    ├── README.md                  <- The top-level README for developers using this project
    ├── app.py                     <- Endpoint to get logs with the given criteria
    ├── config.py                  <- Config variables used during runtime
    ├── docker-compose.yaml        <- Docker compose to create a local deployment 
    ├── Dockerfile                 <- Dockerfile to create log_retrieval_app image
    ├── export_logs.sh             <- Stub bash file to automate archiving of MongoDB documents from local storage to S3
    ├── log_reader.py              <- Class to read logs from S3
    ├── mongodb_gateway.py         <- Class to get logs from MongoDB
    ├── scripts 
    │   ├── dummy_log_generator.py <- Generates dummy logs randomly  
    │   ├── dump_dummy_logs.py     <- Dumps dummy logs to MongoDB
    ├── tests                      <- unit tests


## Run Unit Tests
### Create an environment
```
conda create -n log_retrieval_app python=3.11

conda activate log_retrieval_app

pip install -r requirements.txt
```

### Add repository path to PYTHONPATH 
```
export PYTHONPATH={path_to_your_repo_root}
```

### Run tests
```
py.test tests
```


## Create Local Deployment
- Replace `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `docker-compose.yaml` with `logs_app_user` keys provided
- To Start MongoDB and Log Retrieval App in separate containers run
```
docker-compose up -d
```
- To generate dummy logs run
```
python scripts/dump_dummy_logs.py
```
- Access API on http://127.0.0.1:5000

For demo purposes, select query parameters from following sets:
- `user_id`: 1, 2, 3, 4, 5
- `log_level`: error, info, debug
- `date`: today's date as dummy logs will be generated for today
- `keyword`: any keyword from ML classification metrics, or a word from this text
```
Lorem ipsum dolor sit amet consectetur adipiscing elit Maecenas ullamcorper convallis leo sit amet feugiat ligula viverra eu
```

### To access logs from cold storage 
Currently only logs between 2023-08-27 and 2023-08-28 at `error` level logs are stored. So please query for those dates only.

## Further Improvement Areas
- Support cluster deployment so that the app runs in any environment.
- Automate archiving documents older than 1 day to s3 in `export_logs.sh`.
- Run `export_logs.sh` as a cronjob on the cluster so that documents are archived from MongoDB at the end of every day 
to AWS S3. Run frequency can be adjusted here according to the needs of the client and how many logs generated every 
day. Running daily is an arbitrary selection.
- Store `zip` files instead of `json` files in AWS S3 bucket so that storage in S3 is also optimized.
- Don't expose AWS secrets at `docker-compose.yaml` store them securely (e.g. AWS Key Manager) and retrieve values from 
there whenever needed.



