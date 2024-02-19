import codecs
import json
from datetime import datetime
from typing import Dict, Any


def read_json(src: str) -> Dict:
    """
    Load the content of a .json file into a python dictionary.

    Parameters
    ----------
        src: str
            Path to the .json file.

    Return
    ------
        json_content: dict
            json content loaded from the file.
    """
    with codecs.open(src, encoding='utf-8') as f_in:
        return json.load(f_in)


def write_json(data: Dict, dest: str, pretty: bool = False) -> None:
    """
    Write a python dictionary to a .json file.

    Parameters
    ----------
        data: dict
            A dictionary that represents the content of the .json file.
        dest: str
            Destination path of the .json file.
        pretty: bool, Optional
            If set to true, the .json file will be formatted for humans to read (default is false).
    """
    if pretty:
        content: str = json.dumps(data, indent=2)
    else:
        content: str = json.dumps(data)

    with codecs.open(dest, 'w', encoding='utf-8') as f_out:
        f_out.write(content)


def url_to_file_name(url: str,
                     file_type: str,
                     include_timestamp: bool = True,
                     cut_after: int = 60
                     ) -> str:
    """
    Returns a string as a filename from a number.

    Parameters
    ----------
        url: str
            The url gets converted into a filename
        file_type: str
            The file type defines the ending of the file name (e.g., "html")
        include_timestamp: bool, Optional
            If set to true, the current timestamp is included in the filename (default is "true")
        cut_after: int, Optional
            The main name (excluding timestamp or ending) is cut after the specified number of characters (default
            is 60)

    Return
    ------
        filename : str
            The computed filename.

    """
    file_name: str = url.replace('https://', '').replace('http://', '').replace('/', '_').replace('www.', '')
    file_name = file_name.replace('wwwnc.', '').replace('.html', '').replace('.pdf', '').replace('.', '-')
    file_name = file_name.replace('?', '__').replace('=', '-').replace('#', '-').replace('&', '__')
    file_name = file_name.replace('\n', '__').replace('\\', '__')
    file_name = f'{file_name[:cut_after]}'
    if include_timestamp:
        file_name += f'.{datetime.now().timestamp()}'
    file_name += f'.{file_type}'
    return file_name


def write_text(dest: str, text: str) -> None:
    """
    Writes a text file to the disk.

    Parameters
    ----------
        dest: str
            The file path of the destination file.
        text: str
            The textual content to write.
    """
    with codecs.open(dest, 'w', encoding='utf-8') as f_out:
        f_out.write(text)


def write_file(dest: str, content: Any):
    """
    Write a file to the dist

    Parameters
    ----------
        dest: str
            The file path of the destination file.
        content: Any
            The content to write
    """
    with codecs.open(dest, 'wb') as f_out:
        f_out.write(content)
