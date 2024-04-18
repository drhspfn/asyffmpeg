import os
import tempfile

class TempFile:
    """
    A context manager for creating temporary files.

    This class provides a context manager interface for creating temporary files that are automatically deleted
    when the context is exited. It creates a temporary file using the `tempfile.NamedTemporaryFile` class with
    a custom prefix.

    Usage:
        ```python
        async with TempFile() as temp_file:
            # Use temp_file.name to access the path of the temporary file within the context.
        ```
    Attributes:
        `file`: The temporary file object created by `tempfile.NamedTemporaryFile`.
    """
    def __init__(self):
        self.file = tempfile.NamedTemporaryFile(delete=False,prefix='asyffmpeg_')

    def __str__(self):
        return self.file.name

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        os.remove(self.file.name)