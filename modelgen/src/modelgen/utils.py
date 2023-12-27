""" misc. utilities used elsewhere in the code"""
import logging
import re
import textwrap
import unicodedata
from typing import Final, List

logger = logging.getLogger(__name__)

semver_matcher = re.compile(r"^v?(?P<patch>(?P<minor>(?P<major>\d+)\.\d+)\.\d+)(.+)?$")


def camel_to_snake(name: str) -> str:
    """return the snake_case version of the given CamelCase input string"""
    # Insert underscores before uppercase letters, excluding the first letter
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    # Handle the case where there's a capital letter followed by another capital
    # (or at the end)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def wrap_text(input_text: str, width: int = 75, margin: int = 4) -> str:
    """
    Wrap text with a specified width and left margin.

    :param text: The text to be wrapped.
    :param width: The width for wrapping the text (excluding margin).
    :param margin: The number of spaces to use as the left margin.
    :return: Wrapped text with the specified left margin.
    """
    prefix: Final = " " * margin

    wrapper = textwrap.TextWrapper(
        width=width,
        expand_tabs=False,
        replace_whitespace=True,
        break_long_words=False,
        break_on_hyphens=False,
    )

    # Split the text into a list of paragraphs (separated by newline characters).
    paragraphs = re.split("\n{2,}", input_text)

    # Process each paragraph
    wrapped_text: List[str] = []
    for paragraph in paragraphs:
        if paragraph:
            # Wrap this paragraph, add a left margin, and then add it to the result.
            wrapped_paragraph = wrapper.fill(paragraph)
            indented_paragraph = textwrap.indent(wrapped_paragraph, prefix)
            wrapped_text.append(indented_paragraph)
        wrapped_text.append("")

    # Join all the wrapped paragraphs with newline characters and return.
    return "\n".join(wrapped_text)


def normalize_text(text: str) -> str:
    """try to simplify some text data"""
    text = unicodedata.normalize("NFC", text)

    # Replace various types of quotes with ASCII equivalent
    quotes = {
        "\u2018": "'",  # Left single quotation mark
        "\u2019": "'",  # Right single quotation mark
        "\u201C": '"',  # Left double quotation mark
        "\u201D": '"',  # Right double quotation mark
        "\u00AB": '"',  # Left-pointing double angle quotation mark
        "\u00BB": '"',  # Right-pointing double angle quotation mark
        # Add any other specific quote characters you want to replace
    }
    for quote_char, ascii_char in quotes.items():
        text = text.replace(quote_char, ascii_char)

    # Replace different dash characters with a standard hyphen
    dashes = [
        "\u2013",  # EN DASH
        "\u2014",  # EM DASH
        "\u2212",  # MINUS SIGN
        # Add any other specific dash-like characters you want to replace
    ]
    for dash in dashes:
        text = text.replace(dash, "-")

    # Replace various whitespace characters with a simple space
    spaces = [
        "\u00A0",  # Non-breaking space
        # Add others as needed
    ]
    for space in spaces:
        text = text.replace(space, " ")

    # Remove invisible characters like zero-width spaces, etc.
    invisible_chars = [
        "\u200B",  # Zero-width space
        "\u200C",  # Zero-width non-joiner
        "\u200D",  # Zero-width joiner
        "\u2060",  # Word joiner
        "\uFEFF",  # Byte Order Mark
        # Add any other specific invisible characters you want to remove
    ]
    for inv_char in invisible_chars:
        text = text.replace(inv_char, "")

    # Remove all other non-printable characters
    text = "".join(
        ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in ("\n", " ")
    )
    text = text.encode("iso-8859-15", "replace").decode("iso-8859-15")

    return text
