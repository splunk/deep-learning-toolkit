import json
import re
import sys


def read_chunk(in_file):
    """Attempts to read a single "chunk" from self.in_file.

    Returns
    -------
    None, if EOF during read.
    (metadata, data) : dict, str
        metadata is the parsed contents of the chunk JSON metadata
        payload, and data is contents of the chunk data payload.

    Raises on any exception.
    """
    header_re = re.compile(r'chunked\s+1.0,(?P<metadata_length>\d+),(?P<body_length>\d+)')

    header = in_file.readline().decode('utf-8')

    if len(header) == 0:
        return None

    m = header_re.match(header)
    if m is None:
        raise ValueError('Failed to parse transport header: %s' % header)

    metadata_length = int(m.group('metadata_length'))
    body_length = int(m.group('body_length'))

    metadata_buf = in_file.read(metadata_length)

    if body_length:
        header = in_file.readline()
        data_length = body_length - len(header)
        data = in_file.read(data_length)
    else:
        header, data = None, b""

    metadata = json.loads(metadata_buf)
    return (metadata, header, data)


def write_chunk(out_file, metadata, body=''):
    """Attempts to write a single "chunk" to the given file.

    metadata should be a Python dict with the contents of the metadata
    payload. It will be encoded as JSON.

    body should be a string of the body payload.

    no return, may throw an IOException
    """
    metadata_buf = None
    if metadata:
        metadata_buf = json.dumps(metadata).encode('utf-8')

    metadata_length = len(metadata_buf) if metadata_buf else 0
    # we need the length in the number of bytes
    body = body.encode('utf-8')

    out_file.write(('chunked 1.0,%d,%d\n' % (metadata_length, len(body))).encode('utf-8'))

    if metadata:
        out_file.write(metadata_buf)

    out_file.write(body)
    out_file.flush()


def unmangle_windows_line_endings(file_descriptors):

    # Unmangle line-endings in Windows.

    # N.B. : Windows converts \n to \r such that transport headers do not
    # get received correctly by the CEXC protocol. However, this is really
    # only needed when the IO is actually an object with a file descriptor.
    # Python 2 docs note that file-like objects that don't have real file
    # descriptors should *not* implement a fileno method:

    if sys.platform == "win32":
        import os
        import msvcrt  # pylint: disable=import-error

        for f in file_descriptors:
            fileno = getattr(f, 'fileno', None)
            if fileno is not None:
                if callable(fileno):
                    try:
                        msvcrt.setmode(
                            f.fileno(), os.O_BINARY  # pylint: disable=E1103
                        )  # pylint: disable=E1103 ; the Windows version of os has O_BINARY
                    except ValueError:
                        # This can be safely skipped, as it is raised
                        # from pytest which incorreclty implements a fileno
                        pass
