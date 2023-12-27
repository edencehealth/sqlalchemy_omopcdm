#!/usr/bin/env python3
""" utility for adjusting the generated model's doc comments, base class name,  """
# pylint: disable=invalid-name
import ast
import logging

from .config import Config
from .rtfm import get_omopcdm_descriptions
from .utils import camel_to_snake

logger = logging.getLogger(__name__)

DOC_COMMENT_SPACER = "\n    "


class DocStringInserter(ast.NodeTransformer):
    """class for adding docstrings to class definitions"""

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config
        self.doc_map = get_omopcdm_descriptions(config.base_doc_url)

    def visit_ClassDef(self, node) -> ast.ClassDef:
        """handler called when visiting a ClassDef node"""

        logger.debug("visiting class: %s", node.name)
        # rename the base class
        if node.name == "Base":
            node.name = self.config.base_class_name

        if node.bases and node.name != self.config.base_class_name:
            # in the model classes change the name of the base class to BASE_CLASS_NAME
            node.bases[0] = ast.Name(id=self.config.base_class_name, ctx=ast.Load())

        # Create a new docstring node
        if node.name == self.config.base_class_name:
            # ...for the base class
            new_docstring = ast.Expr(
                value=ast.Constant(
                    value=(
                        f"{DOC_COMMENT_SPACER}"
                        f"{self.config.base_class_desc}"
                        f"{DOC_COMMENT_SPACER}"
                        f"{self.config.base_doc_url}"
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
                        f"{self.config.base_doc_url}"
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


def rename_base_and_add_docstrings(config: Config):
    """add docstrings to the Class definitions in the given model file"""
    filename = config.output_file

    with open(filename, "rt", encoding="utf8", errors="strict") as fh:
        source = fh.read()

    # Parse the source code into an AST
    tree = ast.parse(source)
    # Modify the AST
    tree = DocStringInserter(config).visit(tree)
    # Convert the AST back to source code
    modified_source = ast.unparse(tree)

    # Write the modified source code back to the file
    with open(filename, "wt", encoding="utf8", errors="strict") as fh:
        fh.write(modified_source)
