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


# http https://endpoint/api/city
# http POST https://endpoint/api/city foo = bar
@app.route('/cities', methods=['GET', 'POST'])
def state_of_city_list():
    request = app.current_request
    if request.method == 'GET':
        return {'CITIES_TO_STATE': CITIES_TO_STATE}
    elif request.method == 'POST':
        data_as_json = request.json_body
        for city in data_as_json:
            CITIES_TO_STATE[city] = data_as_json[city]
        return {'CITIES_TO_STATE': CITIES_TO_STATE}


# http PUT https://endpoint/api/city/{city} foo = bar
# http GET https://endpoint/api/city/{city}
@app.route('/city/{city}', methods=['GET', 'PUT'])
def state_of_city_detail(city):
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


# http https://endpoint/api/city_s3
# http POST https://endpoint/api/city_s3 foo = bar
@app.route('/city_s3', methods=['GET', 'POST'])
def state_of_city_list_s3():
    request = app.current_request
    if request.method == 'GET':
        response = S3.get_object(Bucket=BUCKET)
        return json.loads(response['Body'].read())
    elif request.method == 'POST':
        data_as_json = request.json_body
        S3.put_object(Bucket=BUCKET, city=list(data_as_json.keys())[0],
                      Body=json.dumps(request.json_body))
        return data_as_json


# http PUT https://endpoint/api/city_s3/{city} foo = bar
# http GET https://endpoint/api/city_s3/{city}
@app.route('/city_s3/{city}', methods=['GET', 'PUT'])
def state_of_city_detail_s3(city):
    request = app.current_request
    if request.method == 'PUT':
        data_as_json = request.json_body
        S3.put_object(Bucket=BUCKET, city=city,
                      Body=json.dumps(data_as_json))
        # response = S3.get_object(Bucket=BUCKET, city=city)
        return data_as_json
    elif request.method == 'GET':
        try:
            response = S3.get_object(Bucket=BUCKET, city=city)
            return json.loads(response['Body'].read())
        except ClientError:
            raise BadRequestError("Unknown city '%s', valid choices are: %s" % (
                                    city, ', '.join(CITIES_TO_STATE.keys())))


