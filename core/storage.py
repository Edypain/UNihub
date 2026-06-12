from django.conf import settings
from django.core.files.storage import FileSystemStorage

try:
    from cloudinary_storage.storage import RawMediaCloudinaryStorage
except ImportError:
    RawMediaCloudinaryStorage = None

class DynamicRawStorage(RawMediaCloudinaryStorage if (getattr(settings, 'USE_CLOUDINARY', False) and RawMediaCloudinaryStorage) else FileSystemStorage):
    """
    Custom storage backend that uses Cloudinary's RawMediaCloudinaryStorage
    in production (for non-image assets like PDFs, PPTX, slides, etc.)
    and falls back to standard local FileSystemStorage during local development.
    """
    def deconstruct(self):
        return ('core.storage.DynamicRawStorage', [], {})
