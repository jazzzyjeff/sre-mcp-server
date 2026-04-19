from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    azure_devops_org_url: str
    azure_devops_pat: str
    azure_devops_project: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
