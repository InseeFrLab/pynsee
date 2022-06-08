import tempfile
from pathlib import Path

def _initialize_temp_directory():
    """A wrapper to initialize temporary directories
    Returns:
        Nothing, just creates the temporay directories
    """

    temporary_file = tempfile.NamedTemporaryFile(delete=False)
    teldir = tempfile.TemporaryDirectory()
    Path(teldir.name).mkdir(parents=True, exist_ok=True)
    print(f"Data will be stored in the \
        following location: {teldir.name}")
    return temporary_file, teldir