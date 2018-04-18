from neo4j.v1 import GraphDatabase

"""
Deploy to AWS : https://docs.aws.amazon.com/zh_cn/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html
在aws上開啟一個ec2並install neo4j，並將此module deploy to lambda，最後將neo4j driver binding to ec2 of neo4j；
Create topic and Publish topic.
Use SNS to trigger lambda and Inspect the SNS msg aleardy storage in the neo4j database.
"""


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


