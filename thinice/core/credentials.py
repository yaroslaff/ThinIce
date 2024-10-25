class AWSCredentials:
    key_id: str
    secret_key: str
    region: str

    def __init__(self, key_id: str, secret_key: str, region: str):
        self.key_id = key_id
        self.secret_key = secret_key
        self.region = region

    def __repr__(self):
        return f'AWSCredentials(key_id={self.key_id})'