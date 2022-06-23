import boto3

url = 'http://localhost:4566'

dynamoDb = boto3.resource('dynamodb', endpoint_url=url)

dynamoDb = boto3.resource('dynamodb', endpoint_url=url)
greenhouseTable = dynamoDb.create_table(
    TableName='greenhouse',
    KeySchema=[
        {
            'AttributeName': 'plant_id',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'plant_id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'userID',
            'AttributeType': 'S'
        }
    ],
    GlobalSecondaryIndexes=[
        {
            'IndexName': 'cid-index',
            'KeySchema': [
                {
                    'AttributeName': 'userID',
                    'KeyType': 'HASH',
                },
            ],
            'Projection': {
                'ProjectionType': 'ALL',
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 2,
                'WriteCapacityUnits': 2,
            }
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

measurementOutputSensorTable = dynamoDb.create_table(
    TableName='measurement',
    KeySchema=[
        {
              'AttributeName': 'measureID',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'measureID',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

print("Table status: ", greenhouseTable.table_status)
print("Table status: ", measurementOutputSensorTable.table_status)
