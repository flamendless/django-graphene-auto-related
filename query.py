from typing import Optional, List, Dict

from graphql.language import ast
from .string import to_snake_case

# INFO: (Brandon)
"""
USAGE: (see graphql.middleware.select_related_middleware)
    paths = ["edges", "node", "id"]
    data: Optional[Any] = find_ast(info.field_asts[0].selection_set.selections, paths)
    tree = build_tree(data)
"""
def get_selection_set_from_ast(gql: List, paths: List[str], index: int=0) -> Optional[List]:
    if index >= len(paths):
        return gql
    for f in gql:
        if f.name.value != paths[index]:
            continue
        if not f.selection_set:
            return gql
        return get_selection_set_from_ast(f.selection_set.selections, paths, index + 1)


def build_tree(fragments: Dict, gql: List) -> Dict:
    tree: Dict = {"fields": []}

    if not gql:
        return tree

    for d in gql:
        value: str = d.name.value
        name: str = to_snake_case(value)

        if isinstance(d, ast.Field):
            if d.selection_set is None:
                if not name.startswith("__"):
                    tree["fields"].append(name)
                continue
            tree[name] = build_tree(fragments, d.selection_set.selections)

        elif isinstance(d, ast.FragmentSpread):
            if value in fragments:
                fragment: ast.FragmentDefinition = fragments[value]
                if fragment.selection_set is None:
                    if not name.startswith("__"):
                        tree["fields"].append(name)
                    continue
                tree.update(build_tree(fragments, fragment.selection_set.selections))

    return tree
