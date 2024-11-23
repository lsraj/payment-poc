
# pip install flask boto3 pytest unittest-mock
# run: pytest -v

import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
import boto3
from botocore.exceptions import ClientError
from paymentApp import paymentApp

class TestCustomerAPI(unittest.TestCase):

    @patch('boto3.resource')  # Mocking boto3 resource to avoid actual DynamoDB calls
    def test_add_customer_success(self, mock_boto_resource):
        # Simulate a successful DynamoDB put_item response
        mock_dynamo_db = MagicMock()
        mock_table = MagicMock()
        mock_dynamo_db.Table.return_value = mock_table
        mock_table.put_item.return_value = {
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }
        mock_boto_resource.return_value = mock_dynamo_db

        # Test data
        customer_data = {
            'customer_id': 'rajesham3',
            'email': 'rajesham3@abc.com'
        }

        # Send a POST request to add customer
        with paymentApp.test_client() as client:
            response = client.post('/v1/api/customer/add', json=customer_data)

        # Check the status code and response
        self.assertEqual(response.status_code, 200)
        self.assertIn('added successfully', response.json['status'])

    @patch('boto3.resource')
    def test_get_customer_success(self, mock_boto_resource):
        # Simulate a successful DynamoDB get_item response
        mock_dynamo_db = MagicMock()
        mock_table = MagicMock()
        mock_dynamo_db.Table.return_value = mock_table
        mock_table.get_item.return_value = {
            'Item': {
                'customer_id': 'rajesham3',
                'email': 'rajesham3@abc.com'
            }
        }
        mock_boto_resource.return_value = mock_dynamo_db

        # Send a GET request to fetch customer info
        with paymentApp.test_client() as client:
            response = client.get('/v1/api/customer/rajesham3')

        # Check the status code and response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['customer_id'], 'rajesham3')

    @patch('boto3.resource')
    def test_get_customer_not_found(self, mock_boto_resource):
        # Simulate a DynamoDB response with no customer
        mock_dynamo_db = MagicMock()
        mock_table = MagicMock()
        mock_dynamo_db.Table.return_value = mock_table
        mock_table.get_item.return_value = {}
        mock_boto_resource.return_value = mock_dynamo_db

        # Send a GET request to fetch non-existent customer info
        with paymentApp.test_client() as client:
            response = client.get('/v1/api/customer/nonexistent123')

        # Check the status code and response
        self.assertEqual(response.status_code, 404)
        self.assertIn('Customer not found', response.json['error'])

    @patch('boto3.resource')
    def test_add_customer_missing_fields(self, mock_boto_resource):
        # Send POST request with missing customer_id field
        with paymentApp.test_client() as client:
            response = client.post('/v1/api/customer/add', json={'email': 'missingid@example.com'})

        # Check the status code and response
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing required fields', response.json['error'])

    @patch('boto3.resource')
    def test_add_customer_dynamodb_error(self, mock_boto_resource):
        # Simulate a DynamoDB error (e.g., permission issues)
        mock_dynamo_db = MagicMock()
        mock_table = MagicMock()
        mock_dynamo_db.Table.return_value = mock_table
        mock_table.put_item.side_effect = ClientError(
            {"Error": {"Message": "Test DynamoDB error"}}, 'PutItem'
        )
        mock_boto_resource.return_value = mock_dynamo_db

        # Test data
        customer_data = {'customer_id': 'rajesham3', 'email': 'rajesham3@abc.com'}

        # Send a POST request to add customer
        with paymentApp.test_client() as client:
            response = client.post('/v1/api/customer/add', json=customer_data)

        # Check the status code and response
        self.assertEqual(response.status_code, 500)
        self.assertIn('Error occurred', response.json['error'])


if __name__ == '__main__':
    unittest.main()

