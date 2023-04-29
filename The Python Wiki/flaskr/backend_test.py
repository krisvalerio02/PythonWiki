import unittest
from unittest.mock import MagicMock, patch
from google.cloud import storage
from flaskr.backend import Backend
import hashlib


class FirebaseMock:

    def get(self, *args, **vr):
        return None

    def put(self, *args, **vr):
        return None


class BucketClientMock:

    blobnames = [
        "test-user",
        "test-image.jpg",
    ]

    def bucket(self, bucket_name):
        self.bucket_name = bucket_name
        return self

    def blob(self, filename):
        self._blob = filename
        return self

    def exists(self):
        return self._blob in BucketClientMock.blobnames

    def upload_from_string(self, _):
        pass

    def download_as_bytes(self):
        prefixed_password = 'tech_exchange' + 'test-password'
        return hashlib.sha256(prefixed_password.encode()).hexdigest().encode()

    def upload_from_filename(self,
                             filepath,
                             filename="",
                             username="",
                             content_type="text.html"):
        pass

    @property
    def public_url(self):
        return f"https://storage.googleapis.com/test-bucket/{self._blob}"


class TestBackend(unittest.TestCase):

    def setUp(self):
        '''
        Set up method defines mock client, bucket and storage before and after each test method
        '''
        # Mock the storage.Client class and create a Backend instance
        self.backend = Backend('test-bucket', bucket_client=BucketClientMock())

    def test_init(self):
        '''
        Test for init method
        '''
        # Create backend instance and test attributes
        assert self.backend.bucket_name == 'test-bucket'

    def test_sign_up(self):
        '''
        Test for sign up method
        '''

        # Create Backend instance and call the sign_up method
        result = self.backend.sign_up('unknown-user', 'test-password')

        # Assert called once will test various methods during the sign up
        self.assertTrue(result)

    def test_failed_sign_up(self):
        '''
        Test failed sign up method for already signed up user
        '''

        # Create Backend instance and call the sign_up method
        result = self.backend.sign_up('test-user', 'test-password')

        # Assert called once will test various methods during the sign up
        self.assertFalse(result)

    def test_sign_in_success(self):
        '''
        Test for successful sign-in
        '''
        username = 'test-user'
        password = 'test-password'
        result = self.backend.sign_in(username, password)
        self.assertTrue(result)

    def test_sign_in_unknown(self):
        '''
        Test for non-existent user
        '''
        username = 'unknown-user'
        password = 'test-password'
        result = self.backend.sign_in(username, password)
        self.assertFalse(result)

    def test_get_image_success(self):
        '''
        Test for successfully getting an image
        '''
        image_name = 'test-image.jpg'
        result = self.backend.get_image(image_name)
        self.assertEqual(
            result, 'https://storage.googleapis.com/test-bucket/test-image.jpg')

    def test_get_image_fail(self):
        '''
        Test for failing to get an image
        '''
        image_name = 'non-existent-image.jpg'
        result = self.backend.get_image(image_name)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
