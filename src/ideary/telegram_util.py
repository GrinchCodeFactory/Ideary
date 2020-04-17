import bson
from telegram import File

import src.ideary.storage as storage

def store_photo(photo:File, user_id:int):
    from mimetypes import MimeTypes
    mime = MimeTypes()
    storage.store_image(
        file_id=photo.file_id,
        file_name=photo.file_path.split('/')[-1],
        user_id=user_id,
        content_type=mime.guess_type(photo.file_path)[0],
        content=photo.download_as_bytearray(),
    )
    return photo.file_id