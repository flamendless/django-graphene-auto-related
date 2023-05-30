from typing import Dict, List

from .query import get_selection_set_from_ast, build_tree

import logging
logger = logging.getLogger(__name__)

TRAVERSE_QUERY: List = ["edges", "node"]
TRAVERSE_EMPTY: List = []

def select_related_middleware(next, root, info, **kwargs):
    if hasattr(info.context, "tree"):
        return next(root, info, **kwargs)

    field_asts: List = info.field_asts
    if (
        (not field_asts) or
        (field_asts[0].selection_set is None)
    ):
        return next(root, info, **kwargs)

    op: str = info.operation.operation
    traverse_path: List[str] = None

    if op == "query":
        traverse_path = TRAVERSE_QUERY
    elif op == "mutation":
        traverse_path = TRAVERSE_EMPTY

    selections: List = info.field_asts[0].selection_set.selections

    data: List = get_selection_set_from_ast(selections, traverse_path)
    if not data:
        data = get_selection_set_from_ast(selections, TRAVERSE_EMPTY)

    tree: Dict = build_tree(info.fragments, data)

    if data and (op == "mutation"):
        return_node: str = data[0].name.value
        if return_node in tree:
            tree = tree[return_node]

    info.context.tree = tree

    return next(root, info, **kwargs)
