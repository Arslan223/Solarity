from pydantic import BaseSettings, Field, SecretField


class DBSettings(BaseSettings):
    # db name
    db_name: str = Field(env="POSTGRES_DB")
    # db user
    db_user: str = Field(env="POSTGRES_USER")
    # db password
    db_password: str = Field(env="POSTGRES_PW")
    # db host
    db_host: str = Field(env="POSTGRES_HOST")
    # db port
    db_port: int = Field(env="POSTGRES_PORT")


class VKSettings(BaseSettings):
    # api token
    api_token: str = Field(env="VK_API_TOKEN")
