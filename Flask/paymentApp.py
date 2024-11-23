import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from flask import Flask, request, jsonify

paymentApp = Flask(__name__)

# POST method to add a customer
@paymentApp.route('/v1/api/customer/add', methods=['POST'])
def add_customer():

    data = request.get_json()

    # sanitise params
    if not data or 'customer_id' not in data or 'email' not in data:
        return jsonify({"error": "Missing required fields: customer_id or email"}), 400

    # Store customer record in DynamoDB
    cust_record = {
        'customer_id': data['customer_id'],
        'email': data['email']
    }

    try:
        dynamodb = boto3.resource('dynamodb')
        cust_table = dynamodb.Table('Customers')
        resp = cust_table.put_item(Item=cust_record)
        return jsonify({"status": data['customer_id'] + " added successfully"}), resp['ResponseMetadata']['HTTPStatusCode']

    except ClientError as e:
        return jsonify({"error": f"Error occurred: {e.response['Error']['Message']}"}), 500


# GET method retriev customer info based on customer_id
@paymentApp.route('/v1/api/customer/<customer_id>', methods=['GET'])
def get_customer(customer_id):

    if customer_id is None:
        return jsonify({"error": "Invalid customer_id"}), 400

    dynamodb = boto3.resource('dynamodb')

    try:
        cust_table = dynamodb.Table('Customers')
        resp = cust_table.get_item(Key={'customer_id': customer_id})

        # Check if the item exists in the response
        if 'Item' in resp:
            customer = resp['Item']
            return jsonify(customer), 200
        else:
            return jsonify({"error": "Customer not found"}), 404

    except ClientError as e:
        return jsonify({"error": f"Error occurred: {e.response['Error']['Message']}"}), 500

if __name__ == '__main__':
    paymentApp.run(debug=True)
