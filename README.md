# datadog-s3-json-sink
*Schedule Lambda's to sink DataDog metrics to S3*

DataDog provides a nice platform for metrics ingestion and dashboards, but
sometimes it'd be useful to extract portions for either more advanced analysis
in Redshift/Athena or to use alongside other S3 data. This Lambda is made to
be scheduled and will query DataDog to update S3 JSON files with the desired
DataDog Query results.

## Installation

To deploy the datadog-s3-json-sink Lambda to your AWS account, you will need a
fairly recent install of Node, then install the Node packages required:

    $ npm install
    
You will need to ensure your have AWS access and secret keys configured
for serverless:

    $ sls config
    
To deploy the datadog-s3-json-sink lambda:

    $ sls deploy

**Important:** You will need to configure the environment variables in the AWS
Console for the deployed Lambda function with the appropriate DataDog
application and API keys.

## Running

Once datadog-s3-json-sink is deployed to your AWS account, you can run it by
passing an event in the appropriate format to it. This should typically be done
via a scheduled Cloudwatch event with a static payload on a recurring schedule.

Note that DataDog decreases resolution as the time period increases. A 15-minute
time period has 5-second resolution, an hour has 20-second resolution, and a day
has 5-minute resolution.

Example event:

    {
        "query": "avg:system.cpu.user{app:my_appp,env:prod}by{host}",
        "time_period": 15,
        "s3_bucket": "my-metrics-bucket",
        "s3_path": "cpu_stats/gzipd/date={date}/hour={hour}/{uuid}.gz"
    }

**query**
    Datadog query per [their JSON request query string](http://docs.datadoghq.com/graphingjson/#requests).

**time_period**
    Period up to now(ish) to acquire data for, in minutes. The Lambda should be
    run at the rounded time period minutes. For example, a time_period of 5
    minutes should be scheduled to run every 5 minutes starting on the hour.

**s3_bucket**
    S3 Bucket to save output to.

**s3_path**
    Format string to save the filename as. Dynamic parts available in the path
    are ``date`` (YYYY-MM-DD), ``year``, ``hour``, ``minute``, ``uuid``. Note 
    that a single file is always written per Lambda execution.

## Developing

datadog-s3-json-sink is written in Python and deployed via serverless to AWS. To an
extent testing it on AWS is the most reliable indicator it works as
intended. However, there are sets of tests that ensure the Python code
is valid and works with arguments as intended that may be run locally.

Create a Python virtualenv, and install the test requirements:

    $ python3.6 -m venv ddenv
    $ source ddenv/bin/activate
    $ pip install -r test-requirements.txt

The tests can now be run with nose:

    $ nosetests

Note that **you cannot run the sls deploy while the virtualenv is active**
due to how the serverless Python requirements plugin operates.
