# Is My Train Fucked?

A tiny web app that answers the question "Is your train fucked?"

Hint: it probably is.

## Technology

IMTF is written in python and intended to be an
[AWS Lambda](https://aws.amazon.com/lambda/) microservice.
[Apex](http://apex.run) is used for function uploading, version management, and
testing.

## Data Flow

1. MTA information is loaded into DynamoDB every 15 minutes by the `update_log`
   function
2. The `update_s3_site` function is invoked as a DynamoDB INSERT trigger, and a
   new file is written to the IMTF S3 bucket.

Pretty simple!

## "API"

Right now, you can hit an "API" and see the latest train status in a really
crappy format. I'm working on fixing it soon, so stay tuned!
