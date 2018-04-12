from chalice import Chalice, BadRequestError, NotFoundError, Response
import sys
from urllib.parse import urlparse, parse_qs
import json
import boto3
from botocore.exceptions import ClientError

app = Chalice(app_name='helloworld')
app.debug = True
CITIES_TO_STATE = {
    'seattle': 'WA',
    'portland': 'OR',
}
OBJECTS = {
}

S3 = boto3.client('s3', region_name='us-west-2')
BUCKET = 'hello_bucket'


@app.route('/')
def index_get():
    return Response(body='hello world!',
                    status_code=200,
                    headers={'Content-Type': 'text/plain'})


# http https://endpoint/api/cities
# http POST https://endpoint/api/cities foo = bar
@app.route('/cities', methods=['GET', 'POST'])
def state_of_city():
    request = app.current_request
    if request.method == 'GET':
        return {'CITIES_TO_STATE': CITIES_TO_STATE}
    elif request.method == 'POST':
        data_as_json = request.json_body
        for cities in data_as_json:
            CITIES_TO_STATE[cities] = data_as_json[cities]
        return {'CITIES_TO_STATE': CITIES_TO_STATE}


# http PUT https://endpoint/api/cities/{city} foo = bar
# http GET https://endpoint/api/cities/{city}
@app.route('/cities/{city}', methods=['GET', 'PUT'])
def myobject(city):
    request = app.current_request
    if request.method == 'PUT':
        CITIES_TO_STATE[city] = request.json_body[city]
        return {city: CITIES_TO_STATE[city]}
    elif request.method == 'GET':
        try:
            return {city: CITIES_TO_STATE[city]}
        except KeyError:
            raise BadRequestError("Unknown city '%s', valid choices are: %s" % (
                city, ', '.join(CITIES_TO_STATE.keys())))


# The default behavior of a view function supports a request body of application/json.
# Specifying the content_types parameter value to your app.route(). This parameter is a list of acceptable content types.
# http --form POST https://endpoint/api/formtest states=WA states=CA --debug
@app.route('/', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def index_post():
    parsed = parse_qs(app.current_request.raw_body.decode())
    return {
        'states': parsed.get('states', [])
    }


@app.route('/objects/{key}', methods=['GET', 'PUT'])
def s3objects(key):
    request = app.current_request
    if request.method == 'PUT':
        S3.put_object(Bucket=BUCKET, Key=key,
                      Body=json.dumps(request.json_body))
    elif request.method == 'GET':
        try:
            response = S3.get_object(Bucket=BUCKET, Key=key)
            return json.loads(response['Body'].read())
        except ClientError as e:
            raise NotFoundError(key)


