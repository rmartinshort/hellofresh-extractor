from hellofresh_extractor.gsuite.drive.GoogleDriveService import GoogleDriveService
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from typing import Optional, Dict, Any, List
from googleapiclient.errors import HttpError
import os


class GoogleDriveHelper:
    """
    A helper class for interacting with Google Drive, allowing for file uploads,
    folder creation, and permission management.

    Attributes:
        folder_name (str): The name of the top-level folder in Google Drive.
        drive_service (GoogleDriveService): The service object for interacting with Google Drive API.
        top_level_folder_id (str): The ID of the top-level folder.
    """

    def __init__(self, folder_name: str) -> None:
        """
        Initializes the GoogleDriveHelper with the specified folder name.

        Args:
            folder_name (str): The name of the folder to be used as the top-level folder.
        """
        self.folder_name = folder_name
        self.drive_service = GoogleDriveService().build()
        self.top_level_folder_id = self.get_folder_id()

    def get_folder_id_from_name(self, folder_name: str) -> List[Dict[str, str]]:
        """
        Retrieve the ID of a Google Drive folder by its name.

        Args:
            folder_name (str): The name of the folder to search for.

        Returns:
            list: A list of dictionaries containing the folder ID and name.
                  Each dictionary has the keys 'id' and 'name'.
                  If no folder is found, returns an empty list.
        """
        query = f"mimeType = 'application/vnd.google-apps.folder' and trashed = false and name = '{folder_name}'"
        response = (
            self.drive_service.files()
            .list(q=query, spaces="drive", fields="nextPageToken, files(id, name)")
            .execute()
        )
        files = response.get("files", [])
        return files

    def get_file_id_from_name(self, file_name: str) -> List[Dict[str, str]]:
        """
        Retrieve the ID of a file in Google Drive by its name.

        Args:
            file_name (str): The name of the file to search for.

        Returns:
            list: A list of dictionaries containing the file ID and name.
                  Each dictionary has the keys 'id' and 'name'.
                  If no file is found, returns an empty list.
        """
        query = f"mimeType != 'application/vnd.google-apps.folder' and trashed = false and name = '{file_name}'"
        response = (
            self.drive_service.files()
            .list(q=query, spaces="drive", fields="nextPageToken, files(id, name)")
            .execute()
        )
        files = response.get("files", [])
        return files

    def list_all_files(self) -> Optional[List[Dict[str, str]]]:
        """
        List all files in the user's Google Drive.

        This method retrieves all files, paginating through results if necessary.
        Each file's ID and name are printed to the console and collected in a list.

        Returns:
            list: A list of dictionaries, each containing the file ID and name.
                  If an error occurs during the API call, returns None.
        """
        # create drive api client
        files: List[Dict[str, str]] = []
        page_token: Optional[str] = None
        try:
            while True:
                # pylint: disable=maybe-no-member
                response = (
                    self.drive_service.files()
                    .list(
                        spaces="drive",
                        fields="nextPageToken, files(id, name)",
                        pageToken=page_token,
                    )
                    .execute()
                )
                for file in response.get("files", []):
                    # Process change
                    print(f"Found file: {file.get('name')}, {file.get('id')}")

                    file_id = file.get("id")
                    file_name = file.get("name")

                    files.append(
                        {
                            "id": file_id,
                            "name": file_name,
                        }
                    )

                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    break

        except HttpError as error:
            print(f"An error occurred: {error}")
            files = None

        return files

    @staticmethod
    def create_export_link(file_id: str) -> str:
        """
        Creates a direct download link for a file in Google Drive.

        Args:
            file_id (str): The ID of the file.

        Returns:
            str: A direct download link for the file.
        """
        return f"https://drive.google.com/uc?export=download&id={file_id}"

    def get_webview_link(self, file_id: str) -> str:
        """
        Retrieves the web view link for a specified file.

        Args:
            file_id (str): The ID of the file.

        Returns:
            str: The web view link for the file.
        """
        return (
            self.drive_service.files()
            .get(fileId=file_id, fields="webViewLink")
            .execute()["webViewLink"]
        )

    def upload_image(
        self, image_name: str, parent_folder_id: Optional[str] = None
    ) -> str:
        """
        Uploads an image to Google Drive.

        Args:
            image_name (str): The name of the image file to upload.
            parent_folder_id (Optional[str]): The ID of the parent folder. If None, uses the top-level folder.

        Returns:
            str: The ID of the uploaded file.
        """
        # ToDo: check supported image types

        if not parent_folder_id:
            parent_folder_id = self.top_level_folder_id

        file_metadata = {"name": image_name, "parents": [parent_folder_id]}
        media = MediaFileUpload(image_name, mimetype="image/jpg")
        file = (
            self.drive_service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        return file.get("id")

    def create_new_permission(
        self, file_id: str, permission: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Creates a new permission for a specified file.

        Args:
            file_id (str): The ID of the file.
            permission (Dict[str, Any]): The permission details.

        Returns:
            Dict[str, Any]: The result of the permission creation.
        """
        result = (
            self.drive_service.permissions()
            .create(fileId=file_id, body=permission)
            .execute()
        )

        return result

    def create_new_folder(
        self, new_folder_name: str, parent_folder_id: Optional[str] = None
    ) -> str:
        """
        Creates a new folder in Google Drive.

        Args:
            new_folder_name (str): The name of the new folder.
            parent_folder_id (Optional[str]): The ID of the parent folder. If None, uses the top-level folder.

        Returns:
            str: The ID of the newly created folder.
        """
        if parent_folder_id:
            parents = [parent_folder_id]
        else:
            parents = [self.top_level_folder_id]

        folder_metadata = {
            "name": new_folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": parents,
        }

        folder = (
            self.drive_service.files()
            .create(body=folder_metadata, fields="id")
            .execute()
        )
        return folder.get("id")

    def get_folder_id(self) -> str:
        """
        Retrieves the ID of the top-level folder based on the folder name.

        Returns:
            str: The ID of the folder.

        Raises:
            ValueError: If no folder with the specified name is found.
        """
        folder_details = (
            self.drive_service.files()
            .list(
                q=f"mimeType = 'application/vnd.google-apps.folder' and name = '{self.folder_name}'"
            )
            .execute()
        )

        if not folder_details.get("files"):
            raise ValueError(f"No folder called {self.folder_name} is found")

        return folder_details["files"][0].get("id", None)

    def create_basic_document(
        self, document_name: str, parent_folder_id: Optional[str] = None
    ) -> str:
        """
        Creates a new Google Document.

        Args:
            document_name (str): The name of the document.
            parent_folder_id (Optional[str]): The ID of the parent folder. If None, uses the top-level folder.

        Returns:
            str: The ID of the newly created document.
        """
        if not parent_folder_id:
            parent_folder_id = self.top_level_folder_id

        document_metadata = {
            "name": document_name,
            "mimeType": "application/vnd.google-apps.document",
            "parents": [parent_folder_id],
        }
        # make the document
        doc = (
            self.drive_service.files()
            .create(body=document_metadata, fields="id")
            .execute()
        )
        doc_id = doc.get("id")

        return doc_id

    def download_image_files(
        self, folder_id: str, download_path: str = "./downloads", extension="HEIC"
    ) -> List[str]:
        """
        Downloads all image files from a specified Google Drive folder.

        Args:
            folder_id (str): The ID of the Google Drive folder.
            download_path (str, optional): Directory to save downloaded files.

        Returns:
            List[str]: Paths to the downloaded files.
        """

        os.makedirs(download_path, exist_ok=True)

        def get_all_image_files(image_extension=extension):
            """Get all image files from the folder with pagination support."""
            files = []
            page_token = None
            query = f"'{folder_id}' in parents and (name contains '.{image_extension.lower()}' or name contains '.{image_extension.upper()}') and trashed = false"

            while True:
                response = (
                    self.drive_service.files()
                    .list(
                        q=query,
                        spaces="drive",
                        fields="nextPageToken, files(id, name)",
                        pageToken=page_token,
                    )
                    .execute()
                )

                files.extend(response.get("files", []))
                page_token = response.get("nextPageToken")
                if not page_token:
                    break

            return files

        def download_single_file(file_info):
            """Download a single file given its info."""
            file_id, file_name = file_info.get("id"), file_info.get("name")
            file_path = os.path.join(download_path, file_name)

            try:
                with open(file_path, "wb") as f:
                    request = self.drive_service.files().get_media(fileId=file_id)
                    downloader = MediaIoBaseDownload(f, request)

                    done = False
                    while not done:
                        _, done = downloader.next_chunk()

                return file_path
            except Exception as e:
                print(f"Error downloading {file_name}: {e}")
                return None

        try:
            # Get all files first, then download them
            image_files = get_all_image_files(extension)

            # Download each file
            downloaded_paths = []

            for file in image_files:
                file_path = download_single_file(file)
                if file_path:
                    downloaded_paths.append(file_path)
            return downloaded_paths

        except HttpError as error:
            print(f"API error: {error}")
            return []

    def upload_csv_file(
        self, file_path: str, parent_folder_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Uploads a CSV file to Google Drive.

        Args:
            file_path (str): Path to the local CSV file to upload.
            parent_folder_id (Optional[str]): ID of the folder to upload to. If None, uploads to the top-level folder.

        Returns:
            Dict[str, str]: Dictionary containing the uploaded file's ID and name.
        """

        # Get the filename from the path
        file_name = os.path.basename(file_path)

        # If folder_id is provided, set the parent folder
        if not parent_folder_id:
            parent_folder_id = self.top_level_folder_id

        # Prepare file metadata
        file_metadata = {
            "name": file_name,
            "mimeType": "text/csv",
            "parents": [parent_folder_id],
        }

        # Create media object for the file
        media = MediaFileUpload(file_path, mimetype="text/csv", resumable=True)

        try:
            # Upload the file
            file = (
                self.drive_service.files()
                .create(body=file_metadata, media_body=media, fields="id,name")
                .execute()
            )

            print(
                f"Uploaded '{file.get('name')}' to Google Drive (ID: {file.get('id')})"
            )
            return {"id": file.get("id"), "name": file.get("name")}

        except HttpError as error:
            print(f"An error occurred while uploading the file: {error}")
            return {}
