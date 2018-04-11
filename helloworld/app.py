from chalice import Chalice, BadRequestError, NotFoundError

app = Chalice(app_name='helloworld')
app.debug = True
CITIES_TO_STATE = {
    'seattle': 'WA',
    'portland': 'OR',
}
OBJECTS = {
}


@app.route('/')
def index():
    return {'hello': 'world'}


# http https://endpoint/api/cities/{city}
@app.route('/cities/{city}')
def state_of_city(city):
    try:
        return {'state': CITIES_TO_STATE[city]}
    except KeyError:
        raise BadRequestError("Unknown city '%s', valid choices are: %s" % (
            city, ', '.join(CITIES_TO_STATE.keys())))


# http PUT https://endpoint/api/resource/{value}
@app.route('/resource/{value}', methods=['PUT'])
def put_test(value):
    return {"value": value}


#
@app.route('/users', methods=['POST'])
def create_user():
    # This is the JSON body the user sent in their POST request.
    user_as_json = app.current_request.json_body
    # We'll echo the json body back to the user in a 'user' key.
    return {'user': user_as_json}


# echo '{"foo": "bar"}' | http PUT https://endpoint/api/objects/mykey
# http GET https://endpoint/api/objects/mykey
@app.route('/objects/{key}', methods=['GET', 'PUT'])
def myobject(key):
    request = app.current_request
    if request.method == 'PUT':
        OBJECTS[key] = request.json_body
    elif request.method == 'GET':
        try:
            return {key: OBJECTS[key]}
        except KeyError:
            raise NotFoundError(key)


# use current_request object and to_dict method, which returns all the information about the current request as a dictionary.
@app.route('/introspect')
def introspect():
    return app.current_request.to_dict()



