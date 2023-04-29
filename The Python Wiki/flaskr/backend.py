import hashlib


class Backend:
    '''
    Provides an interface for the underlying GCS buckets
    '''

    def __init__(self, bucket_name, bucket_client):
        self.bucket_name = bucket_name
        self.bucket = bucket_client.bucket(bucket_name)

    def get_wiki_page(self, filename):
        '''
        Gets an uploaded page from the content bucket.
        '''
        return "https://storage.googleapis.com/wiki-user-uploads/wiki-user-uploads/" + filename

    def get_all_page_names(self, author):
        '''
        Gets the names of all pages from the content bucket.
        '''
        files = []
        for blob in self.bucket.list_blobs():
            if author in blob.name:
                files.append(blob.name)
        print(files)
        return files

    def get_authors(self):
        '''
        Gets the name of all the authors from the content bucket.
        '''
        files = set()
        for blob in self.bucket.list_blobs():
            files.add(blob.name.split('/')[-2])
        return files

    def upload(self, filepath, filename, username):
        '''
        Adds data to the content bucket.
        '''
        blob = self.bucket.blob(f"wiki-user-uploads/{username}/{filename}")
        blob.upload_from_filename(filepath, content_type="text.html")

    def sign_up(self, username, password):
        '''
        Adds user data if it does not exist along with a hashed password.
        '''
        prefix_for_password = 'tech_exchange'
        prefixed_password = prefix_for_password + password
        hashed_password = hashlib.sha256(prefixed_password.encode()).hexdigest()
        blob = self.bucket.blob(username)
        if blob.exists():
            return False
        else:
            blob.upload_from_string(hashed_password)
            return True

    def sign_in(self, username, password):
        '''
        Checks if a password, when it hashed, matches the password in the user bucket.
        '''
        prefix_for_password = 'tech_exchange'
        prefixed_password = prefix_for_password + password
        hashed_password = hashlib.sha256(prefixed_password.encode()).hexdigest()
        blob = self.bucket.blob(username)
        if blob.exists():
            bucket_password = blob.download_as_bytes().decode('utf-8')
            if hashed_password == bucket_password:
                return True
        else:
            return False

    def get_image(self, image_name):
        '''
        Gets an image from the content bucket.
        '''
        blob = self.bucket.blob(image_name)
        if blob.exists():
            return blob.public_url
        else:
            return None

    def validate_username(self, username):
        '''
        Checks if the username exists in the content bucket
        '''
        blob = self.bucket.blob(username)
        if blob.exists():
            return True
        else:
            return False

    def delete_user(self, username):
        '''
        Creates and deletes a mock user for testing
        '''
        blob_username = username
        blob = self.bucket.blob(blob_username)
        if blob.exists():
            blob.delete()
            return True
        else:
            return False

    def add_comment(self, comment, firebase):
        firebase.post(comment)

    def get_comment_ID(self, current_time, comment):
        comment_id = str(123) + "_" + comment
        return comment_id

    def get_userID(self, username, current_time):
        user_id = str(123) + "_" + username
        return user_id
