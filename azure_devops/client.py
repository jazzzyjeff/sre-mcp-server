from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure_devops.config import settings
from functools import lru_cache


@lru_cache(maxsize=1)
def get_client():
    """Singleton Azure DevOps connection."""
    credentials = BasicAuthentication("", settings.azure_devops_pat)
    connection = Connection(base_url=settings.azure_devops_org_url, creds=credentials)
    return connection
