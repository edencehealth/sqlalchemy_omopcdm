"""access the official OMOP CDM documentation"""
import logging
from typing import Dict

import requests
from bs4 import BeautifulSoup

from .utils import normalize_text, wrap_text

logger = logging.getLogger(__name__)


def get_omopcdm_descriptions(url: str) -> Dict[str, str]:
    """
    return a dict mapping OMOP CDM table names to their text descriptions;
    data is sourced from the given url
    """
    result: Dict[str, str] = {}

    logger.debug("sending request to %s", url)
    response = requests.get(url, timeout=300)
    # Send a GET request to the URL
    # Check if the request was successful
    if response.status_code != 200:
        raise ValueError(
            f"Failed to retrieve the page. Status code: {response.status_code}"
        )
    logger.debug("downloaded %s bytes", len(response.content))

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all div elements with the specified class
    sections = soup.find_all("div", class_="section level3 tabset tabset-pills")

    # Iterate through sections to extract table descriptions
    for section in sections:
        # Find the table name within the h3 tag
        table_name = section.find("h3").text.strip()
        logger.debug("found table %s", table_name)

        # Initialize description content
        description_content = []

        # Start with the node immediately after <strong>Table Description</strong>
        current_node = section.find("p", text="Table Description").find_next_sibling()

        # Loop through siblings until we find a table
        while current_node and current_node.name != "table":
            # Check if the current node is a paragraph and add its text to the
            # description
            if current_node.name == "p":
                content = current_node.text.strip()
                if content:
                    description_content.append(content)
            # Move to the next sibling node
            current_node = current_node.find_next_sibling()

        # Add the table name and description to the map
        result[table_name.lower()] = wrap_text(
            normalize_text("\n\n".join(description_content))
        )

    for k, v in result.items():
        for line in v.splitlines():
            logger.debug("%s: %s", k, line)

    return result
