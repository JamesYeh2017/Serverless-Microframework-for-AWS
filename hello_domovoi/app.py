import json, boto3, domovoi

app = domovoi.Domovoi()


@app.scheduled_function("cron(0 18 ? * MON-FRI *)")
def foo(event, context):
    context.log("foo invoked at 06:00pm (UTC) every Mon-Fri")
    return dict(result=True)


@app.scheduled_function("rate(1 minute)")
def bar(event, context):
    context.log("bar invoked once a minute")
    boto3.resource("sns").create_topic(Name="bartender").publish(Message=json.dumps({"beer": 1}))
    return dict(result="Work work work")


@app.sns_topic_subscriber("bartender")
def tend(event, context):
    message = json.loads(event["Records"][0]["Sns"]["Message"])
    context.log(dict(beer="Quadrupel", quantity=message["beer"]))


@app.cloudwatch_event_handler(source=["aws.ecs"])
def monitor_ecs_events(event, context):
    message = json.loads(event["Records"][0]["Sns"]["Message"])
    context.log("Got an event from ECS: {}".format(message))


@app.s3_event_handler(bucket="myS3bucket", events=["s3:ObjectCreated:*"], prefix="foo", suffix=".bar")
def monitor_s3(event, context):
    message = json.loads(event["Records"][0]["Sns"]["Message"])
    context.log("Got an event from S3: {}".format(message))


# Set use_sns=False to subscribe your Lambda directly to S3 events without forwrading them through an SNS topic.
# That approach has fewer moving parts, but you can only subscribe one Lambda function to events in a given S3 bucket.
@app.s3_event_handler(bucket="myS3bucket", events=["s3:ObjectCreated:*"], prefix="foo", suffix=".bar", use_sns=False)
def monitor_s3(event, context):
    message = json.loads(event["Records"][0]["Sns"]["Message"])
    context.log("Got an event from S3: {}".format(message))


# DynamoDB event format: https://docs.aws.amazon.com/lambda/latest/dg/eventsources.html#eventsources-ddb-update
@app.dynamodb_stream_handler(table_name="MyDynamoTable", batch_size=200)
def handle_dynamodb_stream(event, context):
    context.log("Got {} events from DynamoDB".format(len(event["Records"])))
    context.log("First event: {}".format(event["Records"][0]["dynamodb"]))


# Use the following command to log a CloudWatch Logs message that will trigger this handler:
# python -c'import watchtower as w, logging as l; L=l.getLogger(); L.addHandler(w.CloudWatchLogHandler()); L.error(dict(x=8))'
# See http://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html for the filter pattern syntax
@app.cloudwatch_logs_sub_filter_handler(log_group_name="watchtower", filter_pattern="{$.x = 8}")
def monitor_cloudwatch_logs(event, context):
    print("Got a CWL subscription filter event:", event)


# See http://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html
# See the "AWS Step Functions state machines" section below for a complete example of setting up a state machine.
@app.step_function_task(state_name="Worker", state_machine_definition=state_machine)
def worker(event, context):
    return {"result": event["input"] + 1, "my_state": context.stepfunctions_task_name}

