import boto3
from botocore.exceptions import ClientError

class SecretsManagerClient:
    def __init__(self, region_name:str = None):
        """Initialize the Secrets Manager client.

        Args:
            region_name: AWS region name as a string. If None, it will use the default region set in the environment.
        """
        self.client = boto3.client('secretsmanager', region_name=region_name)

    def get_secret(self, secret_id: str):
        """Retrieve a secret from AWS Secrets Manager.

        Args:
            secret_id (str): The ID or name of the secret to retrieve.

        Returns:
            str: Secret value as a string.

        Raises:
            ValueError: If the secret cannot be found.
            ClientError: If an AWS error is encountered.
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
            return response['SecretString']
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise ValueError("Secret not found: {}".format(secret_id))
            else:
                raise
