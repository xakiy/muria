"""Multipart File Save."""

import shutil
import os
import mimetypes
import magic
from uuid import UUID
from pathlib import Path
from muria import config, logger


class FormStore(object):
    """
    Store file upload via mutlipart/form-data request.

    Currently does not support "multiple" files input,
    only save one file per field name.
    """

    def __init__(self, config=config):
        self.temp_dir = config.get("dir_temp")

    def save(self, input_handler, dest_dir):
        # We should sanitize dest_dir as if someone will
        # use in arbitrary way
        logger.info("Saving uploaded file...")
        temp_name = os.urandom(24).hex()

        # Read file as binary
        raw = input_handler.file

        # Retrieve filetype
        source_type = input_handler.type
        logger.info("Source Type: {0}".format(source_type))

        # Retrieve file extension
        source_ext = Path(input_handler.filename).suffix
        # BUG: doesn't yet support multi extension ie. .tar.gz
        logger.info("Source Ext: {0}".format(source_ext))

        # To prevent incomplete files from being used we write it
        # first as temporary one.
        temp_file = Path(self.temp_dir, temp_name).with_suffix(".tmp")
        logger.info("Temporary File Path: {0}".format(temp_file))

        try:
            # Then write the stream data to that temporary file
            temp_obj = open(temp_file, "x+b")

            shutil.copyfileobj(raw, temp_obj)

            # If done writing, grab the extension
            temp_obj.seek(0)
            extensions = mimetypes.guess_all_extensions(
                magic.from_buffer(temp_obj.read(128), mime=True)
            )

            temp_obj.close()

            ext = source_ext if source_ext in extensions else extensions[0]
            new_file = Path(dest_dir, temp_name).with_suffix(ext)
            # Now that we know the file has been fully saved to disk
            # and we can rename/move it.
            temp_file.rename(new_file)

        except FileNotFoundError as nof:
            logger.debug('Error: {0} of "{1}"'.format(nof.strerror, new_file))
            return None

        logger.info("New File Path: {0}".format(new_file))
        return new_file.name

    def delete(self, filename):
        obj = Path(filename)
        if obj.is_file():
            obj.unlink()
        return not obj.exists()


class StreamStore(object):

    def __init__(self, config=config):
        self.dest_dir = config.get("dir_image")

    def save(self, image_stream, image_content_type):
        ext = mimetypes.guess_extension(image_content_type)
        temp_file = Path(self._dest_dir, os.urandom(24).hex()).with_suffix(ext)

        with temp_file.open(mode="wb") as obj_file:
            while True:
                chunk = image_stream.read(4096)
                if not chunk:
                    break
                obj_file.write(chunk)

        return temp_file.stem

    def open(self, name):

        file = Path(self.dest_dir, name)
        if not UUID(file.stem) and file.exists():
            raise IOError("File not found")
        stream = open(file, "rb")
        return stream, file.stat().st_size
