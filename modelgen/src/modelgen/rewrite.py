#!/usr/bin/env python3
""" utility for adjusting the generated model's doc comments, base class name,  """
# pylint: disable=invalid-name
import logging
from typing import Sequence

import libcst as cst

from .config import Config
from .rtfm import get_omopcdm_descriptions
from .utils import camel_to_snake

logger = logging.getLogger(__name__)

DOC_COMMENT_SPACER = "\n    "


class ModelRewriter(cst.CSTTransformer):
    """class for adding docstrings to class definitions"""

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config
        self.doc_map = get_omopcdm_descriptions(config.base_doc_url)

    def leave_Module(
        self,
        original_node: cst.Module,
        updated_node: cst.Module,
    ) -> cst.Module:
        """add a module doc string and some comments"""
        # module docstring
        mod_docstring = "OMOP Common Data Model v5.4 DeclarativeBase SQLAlchemy models"
        docstring = cst.SimpleStatementLine(
            body=[cst.Expr(cst.SimpleString(f'"""{mod_docstring}"""'))]
        )

        # pylint-disable comments
        disabled: Sequence[str] = (
            "too-few-public-methods",
            "too-many-lines",
            "unnecessary-pass",
            "unsubscriptable-object",
        )
        pylint_comments = [
            cst.EmptyLine(comment=cst.Comment(f"# pylint: disable={check}"))
            for check in disabled
        ]
        # Insert the docstring and comments at the beginning of the module body
        new_body = [docstring] + pylint_comments + list(updated_node.body)

        return updated_node.with_changes(body=new_body)

    def leave_ClassDef(
        self,
        original_node: cst.ClassDef,
        updated_node: cst.ClassDef,
    ) -> cst.ClassDef:
        """Handler called when leaving a ClassDef node."""
        class_name = updated_node.name.value

        # Rename the base class, if necessary
        if class_name == "Base":
            updated_node = updated_node.with_changes(
                name=cst.Name(self.config.base_class_name)
            )
            class_name = updated_node.name.value

        # Update the base class for model classes
        if updated_node.bases and class_name != self.config.base_class_name:
            updated_node = updated_node.with_changes(
                bases=[cst.Arg(value=cst.Name(value=self.config.base_class_name))]
            )

        # Create a new docstring node
        if class_name == self.config.base_class_name:
            docstring_value = (
                f"{DOC_COMMENT_SPACER}"
                f"{self.config.base_class_desc}"
                f"{DOC_COMMENT_SPACER}"
                f"{self.config.base_doc_url}"
                f"{DOC_COMMENT_SPACER}"
            )
        else:
            snake_case_name = camel_to_snake(class_name)
            link_fragment = snake_case_name.upper()
            table_description = self.doc_map.get(snake_case_name, "")
            docstring_value = (
                f"\n{table_description}"
                f"{DOC_COMMENT_SPACER}"
                f"{self.config.base_doc_url}"
                f"#{link_fragment}"
                f"{DOC_COMMENT_SPACER}"
            )

        new_docstring = cst.SimpleStatementLine(
            body=[cst.Expr(value=cst.SimpleString(f'"""{docstring_value}"""'))]
        )

        # Insert the docstring at the start of the class body, if it's an IndentedBlock
        if isinstance(updated_node.body, cst.IndentedBlock):
            new_body = [new_docstring] + list(updated_node.body.body)
            return updated_node.with_changes(body=cst.IndentedBlock(body=new_body))
        # If it's not an IndentedBlock, this might not be the correct place to handle it
        # You might want to log an error or handle this case differently
        return updated_node


def rename_base_and_add_docstrings(config: Config):
    """add docstrings to the Class definitions in the given model file"""
    filename = config.output_file

    with open(filename, "rt", encoding="utf8", errors="strict") as fh:
        source = fh.read()

    # parse the source code into a CST
    rewriter = ModelRewriter(config)
    # modify the CST
    modified_tree = cst.parse_module(source).visit(rewriter)

    # Write the modified source code back to the file
    with open(filename, "wt", encoding="utf8", errors="strict") as fh:
        fh.write(modified_tree.code)
