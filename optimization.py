from typing import Optional, Dict, List, Any, KeysView, Tuple
from pprint import pprint

from django.db.models import QuerySet
from django.db.models.fields.related_descriptors import ReverseManyToOneDescriptor

from saleor.core.utils.string import to_snake_case


def get_valid_fields(
    model: Any,
    tree: Dict,
    keys: KeysView,
    root: Any=None
) -> Tuple[List[str], List[str]]:
    valid_keys: List[str] = []
    valid_fields: List[str] = []

    for field in keys:
        if (field == "fields"):
            continue

        if hasattr(model, field):
            if isinstance(getattr(model, field), ReverseManyToOneDescriptor):
                continue

            valid_fields.append(field)
            continue

        if (root is not None) and (hasattr(root, field)):
            next_keys: KeysView = tree[field].keys()
            others, other_keys = get_valid_fields(model, tree, next_keys, root)
            if others:
                valid_keys.append(field)
                valid_fields.extend(others)

            if other_keys:
                valid_keys.extend(other_keys)

    return valid_fields, valid_keys


def auto_related(qs: QuerySet, info, root: Any=None) -> QuerySet:
    tree: Optional[Dict] = getattr(info.context, "tree", None)
    if not tree:
        return qs

    model: Any = qs.query.model
    sc: str = to_snake_case(model.__name__)
    keys: KeysView = (
        tree[sc].keys()
        if (sc in tree)
        else tree.keys()
    )

    valid_fields, valid_keys = get_valid_fields(model, tree, keys, root)
    if not valid_fields:
        return qs

    if valid_keys:
        for vf, vk in zip(valid_fields, valid_keys):
            subtree: Dict = tree[vk][vf]
            subkeys: List[str] = [
                subkey
                for subkey in subtree.keys()
                if subkey != "fields"
            ]
            additional_fields: List[str] = [
                f"{vf}__{subkey}"
                for subkey in subkeys
            ]
            valid_fields.extend(additional_fields)

    return qs.select_related(*valid_fields)
