from typing import Optional, Dict, List, Any, KeysView

from django.db import models
from django.db.models.fields.related_descriptors import ReverseManyToOneDescriptor
from .string import to_snake_case


def get_valid_fields(model: Any, tree: Dict, keys: KeysView, root: Any=None) -> List[str]:
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
            others: List[str] = get_valid_fields(model, tree, next_keys, root)
            valid_fields.extend(others)

    return valid_fields


def auto_related(qs: models.QuerySet, info, root: Any=None) -> models.QuerySet:
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

    valid_fields: List[str] = get_valid_fields(model, tree, keys, root)
    if not valid_fields:
        return qs

    return qs.select_related(*valid_fields)
