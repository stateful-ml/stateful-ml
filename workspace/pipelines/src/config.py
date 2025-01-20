from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    EnvSettingsSource,
)
from pydantic import Field
from pydantic.fields import FieldInfo

from prefect.blocks.system import Secret
from typing import Any


class PrefectSettingsSource(EnvSettingsSource):
    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        field_info = self._extract_field_info(field, field_name)
        assert len(field_info) > 0, "unreachable"

        env_val: str | None = None
        for field_key, env_name, value_is_complex in field_info:
            for name_format in [env_name, env_name.replace("_", "-").lower()]:
                try:
                    env_val = Secret.load(name_format, validate=False).get()
                    break
                except ValueError:
                    pass
            if env_val is not None:
                break

        return env_val, field_key, value_is_complex  # type: ignore


def prefect_secret_source(settings: BaseSettings) -> dict:
    """
    Custom source to fetch secrets from Prefect's secret store.
    """
    secrets = {}
    for field in settings.model_fields:
        try:
            secrets[field] = Secret.load(field).get()
        except Exception:
            pass
    return secrets


class Config(BaseSettings):
    source_users_table: str = Field(alias='USERS_TABLE')
    mlflow_tracking_uri: str
    supabase_url: str
    supabase_key: str
    vectorstore_connection_string: str
    content_bucket: str

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ):
        # Include the custom source
        return (
            init_settings,
            PrefectSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


config = Config.model_validate({})
print(config)
