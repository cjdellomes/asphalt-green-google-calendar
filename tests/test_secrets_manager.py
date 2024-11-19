import unittest
from unittest.mock import patch
from botocore.exceptions import ClientError
from source.secretsmanager import SecretsManagerClient

class TestSecretsManagerClient(unittest.TestCase):
    """Tests for the SecretsManagerClient class"""

    @patch('boto3.client')
    def test_get_secret_successful_retrieval(self, mock_client):
        """Test method for the get_secret function assuming successful SM call and retrieval"""
        mock_client.return_value.get_secret_value.return_value = {
            'SecretString': 'test-value'
        }

        result = SecretsManagerClient().get_secret('test-id')

        self.assertEqual(result, 'test-value')

    @patch('boto3.client')
    def test_get_secret_cannot_find_secret(self, mock_client):
        """Test method for the get_secret function assuming non-existant secret"""
        mock_client.return_value.get_secret_value.side_effect = ClientError({
            'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Secret not found'}
        }, 'GetSecretValue')

        with self.assertRaises(ValueError) as context:
            SecretsManagerClient().get_secret('nonexistentid')

        self.assertTrue('Secret not found' in str(context.exception))

    @patch('boto3.client')
    def test_get_secret_failed_aws_call(self, mock_client):
        """Test method for the get_secret function assuming a failed call to SM"""
        mock_client.return_value.get_secret_value.side_effect = ClientError({
            'Error': {'Code': 'InternalServiceError', 'Message': 'An internal error occurred'}
        }, 'GetSecretValue')

        with self.assertRaises(ClientError) as context:
            SecretsManagerClient().get_secret('badrequestid')

        self.assertTrue('An internal error occurred' in str(context.exception))

if __name__ == '__main__':
    unittest.main()
