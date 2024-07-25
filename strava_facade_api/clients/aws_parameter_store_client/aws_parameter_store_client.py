import boto3


class ParameterStoreClient:
    def __init__(self) -> None:
        self.client = boto3.client("ssm")

    def get_parameter(self, path: str) -> str:
        parameter = self.client.get_parameter(Name=path)
        return parameter["Parameter"]["Value"]

    def get_secret(self, path: str) -> str:
        parameter = self.client.get_parameter(Name=path, WithDecryption=True)
        return parameter["Parameter"]["Value"]

    def put_parameter(self, path: str, value: str, do_overwrite=False) -> None:
        self.client.put_parameter(
            Name=path,
            Description="string",
            Value=value,
            Type="String",
            Overwrite=do_overwrite,
        )

    def put_secret(self, path: str, value: str, do_overwrite=False) -> None:
        self.client.put_parameter(
            Name=path,
            Description="string",
            Value=value,
            Type="SecureString",
            Overwrite=do_overwrite,
        )
