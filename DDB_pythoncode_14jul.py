import boto3
import json
import os
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def create_transaction(transaction_data):
    """Create a new transaction record"""
    transaction_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    try:
        item = {
            'PK': f"TRANS#{transaction_id}",
            'SK': 'METADATA',
            'customerId': f"CUST#{transaction_data['customer_id']}",
            'status': transaction_data.get('status', 'PENDING'),
            'creationTime': timestamp,
            'transactionType': transaction_data.get('transaction_type'),
            'deliveryId': f"DEL#{str(uuid.uuid4())}" if 'delivery_id' not in transaction_data else f"DEL#{transaction_data['delivery_id']}",
            'entityType': 'TRANSACTION',
            'GSI1PK': f"CUST#{transaction_data['customer_id']}",
            'GSI1SK': f"TRANS#{timestamp}"
        }
        
        table.put_item(Item=item)
        return item
        
    except ClientError as e:
        print(f"Error creating transaction: {e.response['Error']['Message']}")
        raise

def lambda_handler(event, context):
    """Main Lambda handler"""
    try:
        # Parse the incoming event
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        
        operation = body.get('operation')
        data = body.get('data', {})
        
        if operation == 'create_transaction':
            result = create_transaction(data)
            response = {
                'transaction_id': result['PK'].split('#')[1],
                'delivery_id': result['deliveryId'].split('#')[1]
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid operation'})
            }
            
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }