"""Azure DevOps configuration settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Azure DevOps connection settings."""

    azure_devops_org_url: str
    azure_devops_pat: str
    azure_devops_project: str = ""

    class Config:
        """Pydantic config."""

        env_file = ".env"
        extra = "ignore"


settings = Settings()
