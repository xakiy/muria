import os
from io import BytesIO

# initialize env testing configurations
try:
    os.environ["MURIA_CONFIG"]
except KeyError:
    os.environ["MURIA_CONFIG"] = os.path.join(
        os.path.dirname(__file__), "settings.ini"
    )


def create_multipart(data, fieldname, filename, content_type):
    """
    Basic emulation of a browser's multipart file upload
    Ref: https://stackoverflow.com/questions/42786531/simulate-multipart-form-data-file-upload-with-falcons-testing-module
    Creator:
    """
    boundry = "----WebKitFormBoundary" + os.urandom(12).hex()
    buff = BytesIO()
    buff.write(b"--")
    buff.write(boundry.encode())
    buff.write(b"\r\n")
    buff.write(
        (
            'Content-Disposition: form-data; name="%s"; filename="%s"'
            % (fieldname, filename)
        ).encode()
    )
    buff.write(b"\r\n")
    buff.write(("Content-Type: %s" % content_type).encode())
    buff.write(b"\r\n")
    buff.write(b"\r\n")
    buff.write(data)
    buff.write(b"\r\n")
    buff.write(boundry.encode())
    buff.write(b"--\r\n")
    headers = {"Content-Type": "multipart/form-data; boundary=%s" % boundry}
    headers["Content-Length"] = str(buff.tell())
    return buff.getvalue(), headers
