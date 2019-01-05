
class InvalidArgumentsException(Exception):
    def __init__(self):
        raise Exception("""
Invalid Arguments Provided.

Example Usage:

    python tako.py input/ output.npy labels.txt 512 512

Arguments:

    input_directory - Directory where your input image files are stored
    output_file - .npy file to store the output classifications
    labels_file - .txt file where labels for each classification are stored in the format
        label1
        label2
        ...
        labelx
    window_height - Height of your selections in the GUI
    window_width - Height of your selections in the GUI
    reset (optional) - if provided as the string "reset", will prompt you to restart your session.
""")

class InvalidLabelsException(Exception):
    def __init__(self):
        raise Exception("""
Invalid Labels Provided.

Example Label File:

    labels.txt:
    ```
    Melanoma
    Carcinoma
    Healthy Skin
    Empty Slide
    Miscellaneous
    ```

    There must be at least one label, there must be no empty lines or labels, and there must be no duplicate labels.
""")

    



