#!/usr/bin/env python3
""" utility for adjusting the generated model's doc comments, base class name,  """
# pylint: disable=invalid-name
import ast
import logging

from .rtfm import get_omopcdm_descriptions
from .utils import camel_to_snake

logger = logging.getLogger(__name__)

BASE_DOC_URL = "https://ohdsi.github.io/CommonDataModel/cdm54.html"
DOC_COMMENT_SPACER = "\n    "
BASE_CLASS_NAME = "OMOPCDMModelBase"
BASE_CLASS_DESC = "Base for OMOP Common Data Model v5.4 Models"


class DocStringInserter(ast.NodeTransformer):
    """class for adding docstrings to class definitions"""

    def __init__(self) -> None:
        super().__init__()
        self.doc_map = get_omopcdm_descriptions(BASE_DOC_URL)

    def visit_ClassDef(self, node) -> ast.ClassDef:
        """handler called when visiting a ClassDef node"""
        print(f"Visiting class: {node.name}")

        # rename the base class
        if node.name == "Base":
            node.name = BASE_CLASS_NAME

        if node.bases and node.name != BASE_CLASS_NAME:
            # Change the name of the first base class
            node.bases[0] = ast.Name(id=BASE_CLASS_NAME, ctx=ast.Load())

        # Create a new docstring node
        if node.name == BASE_CLASS_NAME:
            # ...for the base class
            new_docstring = ast.Expr(
                value=ast.Constant(
                    value=(
                        f"{DOC_COMMENT_SPACER}"
                        f"{BASE_CLASS_DESC}"
                        f"{DOC_COMMENT_SPACER}"
                        f"{BASE_DOC_URL}"
                        f"{DOC_COMMENT_SPACER}"
                    )
                )
            )
        else:
            # ...for the model classes
            snake_case_name = camel_to_snake(node.name)
            link_fragment = snake_case_name.upper()
            table_description = self.doc_map[snake_case_name]
            new_docstring = ast.Expr(
                value=ast.Constant(
                    value=(
                        f"\n{table_description}"
                        f"{DOC_COMMENT_SPACER}"
                        f"{BASE_DOC_URL}"
                        f"#{link_fragment}"
                        f"{DOC_COMMENT_SPACER}"
                    ),
                    type=None,
                )
            )

        # replace or insert the docstring node
        if docstring := ast.get_docstring(node):
            # replace existing docstring
            if docstring != node.body[0].value.value.strip():
                raise ValueError(
                    "Node has docstring but it isn't at body[0]; "
                    f"{docstring!r} vs {node.body[0].value.value.strip()!r}"
                )
            node.body[0] = new_docstring
        else:
            # Insert the docstring at the start of the function body
            node.body.insert(0, new_docstring)

        # Don't forget to return the modified node!
        return node


def add_docstrings_to_file(filename):
    """add docstrings to the Class definitions in the given model file"""
    with open(filename, "rt", encoding="utf8", errors="strict") as fh:
        source = fh.read()

    # Parse the source code into an AST
    tree = ast.parse(source)
    # Modify the AST
    tree = DocStringInserter().visit(tree)
    # Convert the AST back to source code
    modified_source = ast.unparse(tree)

    # Write the modified source code back to the file
    with open(filename, "wt", encoding="utf8", errors="strict") as fh:
        fh.write(modified_source)
