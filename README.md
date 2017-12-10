# Is My Train Fucked?

A tiny web app that answers the question "Is your train fucked?"

Hint: it probably is.

## Technology

IMTF is written in python and intended to be an
[AWS Lambda](https://aws.amazon.com/lambda/) microservice.
[Apex](http://apex.run) is used for function uploading, version management, and
testing.

## Data Flow

1. MTA information is queried every minute
   
   a. New data is written to S3 for record-keeping purposes (perhaps querying w/ Atlas in the future?)

   b. New data is written to index.html file and uploaded to S3 hosted website

Pretty simple!

## "API"

Right now, you can hit an "API" and see the latest train status in a really
crappy format. I'm working on fixing it soon, so stay tuned!
