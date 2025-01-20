from pydantic_settings import BaseSettings


class Config(BaseSettings):
    version: str
    vectorstore_connection_string: str
    preference_updater_identifier: str


config = Config.model_validate({})
