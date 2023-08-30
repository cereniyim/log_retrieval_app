# bash file to dump logs to AWS S3 "ceren-logs-v1" bucket daily. The aim is to optimize storage of MongoDB.

# It generates a json file that is indexed by date, user_id and log_level. And archives dumped files from MongoDB.

# It accepts following parameters, to connect AWS S3

# - AWS_ACCESS_KEY
# - AWS_SECRET_ACCESS_KEY_ID

# Then executes following steps:
# 1) Queries all user IDs
# 2) Per user ID, filters documents by today's date, log_level and user ID. Log level will be statically defined as
#    ["info", "debug", "error"].
# 3) Saves the file with the following format `archive_logs_<date>_<user_id>_<log_level>.json` to `s3://ceren-logs-v1/`
# 4) Deletes the dumped documents from MongoDB

# this sh file can run on the cluster with every 24h at the end of the day as a cronjob, this way MongoDB is used
# efficiently as hot storage, and AWS bucket is used as a cold storage.