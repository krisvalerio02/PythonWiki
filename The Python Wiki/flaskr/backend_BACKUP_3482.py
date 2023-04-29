from google.cloud import storage


class Backend:

    def __init__(self, project_id, bucket_name):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.client = storage.Client(project=project_id)
        self.bucket = self.client.bucket(bucket_name)

    def get_wiki_page(self, name):
        pass

    def get_all_page_names(self):
        page_names = self.bucket.list_blobs()
        return [f.name for f in page_names]

    def upload(self, file_path):
        blob = self.bucket.blob(file_path)
        blob.upload_from_filename(file_path)

    def sign_up(self):
        pass

    def sign_in(self):
        pass

    def get_image(self, image_name):
        """Gets an image from the image bucket."""
        blob = self.bucket.blob(image_name)
        if blob.exists():
            return blob.download_as_bytes()
        else:
            return None
