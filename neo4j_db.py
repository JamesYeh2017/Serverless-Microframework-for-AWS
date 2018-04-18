from neo4j.v1 import GraphDatabase


def handler(event, context):

    message = event['Records'][0]['Sns']['Message']
    messageid = event['Records'][0]['Sns']['MessageId']

    # connection and insert data
    driver = GraphDatabase.driver("bolt://$neo4j_ip:port", auth=("neo4j", "neo4j"))  # $neo4j_ip :
    session = driver.session()
    session.run("CREATE (a:Person {{name: '{}', title: 'Test'}})".format(message))

    result = session.run("MATCH (a:Person) WHERE a.name = '{}' RETURN a.name AS name, a.title AS title".format(message))
    for record in result:
        print('{}{}'.format(record["title"], record["name"]))

    session.close()

    return 'SUCCESS'


