from google.oauth2 import service_account
from abc import ABC, abstractmethod
from hellofresh_extractor.gsuite.base.config import CREDENTIALS
from typing import Any


class GSuiteService(ABC):
    """
    An abstract base class for G Suite services.

    This class defines the structure for any G Suite service implementation,
    requiring subclasses to specify the scopes and service creation logic.

    Attributes:
        credential_path (str): The path to the credentials file.
        SCOPES (list): The scopes required for the service.
    """

    def __init__(self) -> None:
        """
        Initializes the GSuiteService with the credential path and scopes.
        """
        # The name of the file containing your credentials
        self.credential_path = CREDENTIALS
        self.SCOPES = self.get_scopes()

    @abstractmethod
    def get_scopes(self) -> list[str]:
        """
        Retrieves the scopes required for the G Suite service.

        Returns:
            list[str]: A list of scopes required for the service.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def get_service(self, credentials: Any) -> Any:
        """
        Creates and returns the service object for the G Suite service.

        Args:
            credentials (Any): The credentials to use for the service.

        Returns:
            Any: The service object for the G Suite service.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def build(self) -> Any:
        """
        Builds the G Suite service using the provided credentials.

        Returns:
            Any: The constructed service object.
        """
        # Get credentials into the desired format
        creds = service_account.Credentials.from_service_account_file(
            self.credential_path, scopes=self.SCOPES
        )

        service = self.get_service(creds)
        return service
