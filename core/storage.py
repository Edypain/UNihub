from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Determine target base storage dynamically based on settings
if getattr(settings, 'USE_SUPABASE_STORAGE', False):
    from storages.backends.s3 import S3Storage
    BaseStorage = S3Storage
elif getattr(settings, 'USE_CLOUDINARY', False):
    try:
        from cloudinary_storage.storage import RawMediaCloudinaryStorage
        BaseStorage = RawMediaCloudinaryStorage
    except ImportError:
        BaseStorage = FileSystemStorage
else:
    BaseStorage = FileSystemStorage

class DynamicRawStorage(BaseStorage):
    """
    Custom storage backend that uses the configured cloud storage in production
    (Supabase or Cloudinary) and falls back to standard local FileSystemStorage
    during local development.
    """
    def deconstruct(self):
        return ('core.storage.DynamicRawStorage', [], {})

