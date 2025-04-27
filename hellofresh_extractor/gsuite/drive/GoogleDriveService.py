from hellofresh_extractor.gsuite.base.GSuiteService import GSuiteService
from googleapiclient.discovery import build
from typing import Any


class GoogleDriveService(GSuiteService):
    """
    A service class for interacting with Google Drive API.

    Inherits from GSuiteService and implements the methods to retrieve
    the required scopes and create the Google Drive service.

    Methods:
        get_scopes: Returns the scopes required for Google Drive API.
        get_service: Creates and returns the Google Drive service object.
    """

    def get_scopes(self) -> list[str]:
        """
        Retrieves the scopes required for the Google Drive service.

        Returns:
            list[str]: A list containing the required scopes for Google Drive API.
        """
        SCOPES = ["https://www.googleapis.com/auth/drive"]
        return SCOPES

    def get_service(self, creds: Any) -> Any:
        """
        Creates and returns the Google Drive service object.

        Args:
            creds (Any): The credentials to use for the Google Drive service.

        Returns:
            Any: The Google Drive service object.
        """
        return build("drive", "v3", credentials=creds, cache_discovery=False)
