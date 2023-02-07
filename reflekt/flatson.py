# SPDX-FileCopyrightText: 2015 ScrapingHub
#
# SPDX-License-Identifier: BSD-3-Clause

# This file contains derivative works based on:
# https://github.com/scrapinghub/flatson/blob/master/flatson/flatson.py
#
# Changes include removal of automatic sorting in the following functions and methods:
#    - infer_flattened_field_names()
#    - extract_key_values()
#    - Flatson._serialize_array_value()


from __future__ import absolute_import, print_function, unicode_literals

import json
from collections import OrderedDict, namedtuple


# flake8: noqa
class Field(namedtuple("Field", "name getter schema")):
    def is_array(self):
        return self.schema.get("type") == "array"

    def is_simple_list(self):
        if not self.is_array():
            return False

        items_type = self.schema.get("items", {}).get("type")
        return items_type in ("number", "string")

    @property
    def serialization_options(self):
        return self.schema.get("flatson_serialize") or {}


def create_getter(path, field_sep="."):
    if field_sep in path:
        first_key, rest = path.split(field_sep, 1)
        return lambda x: create_getter(rest)(x.get(first_key, {}))
    else:
        return lambda x: x.get(path, None)


def infer_flattened_field_names(schema, field_sep="."):
    fields = []

    for key, value in schema.get("properties", {}).items():
        val_type = value.get("type")
        if val_type == "object":
            for subfield in infer_flattened_field_names(value):
                full_name = "{prefix}{fsep}{extension}".format(
                    prefix=key, fsep=field_sep, extension=subfield.name
                )
                fields.append(
                    Field(full_name, create_getter(full_name), subfield.schema)
                )
        else:
            fields.append(Field(key, create_getter(key), value))

    return fields
    # return sorted(fields)


def extract_key_values(array_value, separators=(";", ",", ":"), **kwargs):
    """Serialize array of objects with simple key-values"""
    items_sep, fields_sep, keys_sep = separators
    return items_sep.join(
        fields_sep.join(keys_sep.join(x) for x in it.items())
        # fields_sep.join(keys_sep.join(x) for x in sorted(it.items()))
        for it in array_value
    )


def extract_first(array_value, **kwargs):
    if array_value:
        return array_value[0]


def join_values(array_value, separator=",", **kwargs):
    return separator.join(str(x) for x in array_value)


class Flatson(object):
    """This class implements flattening of JSON objects"""

    _default_serialization_methods = {
        "extract_key_values": extract_key_values,
        "extract_first": extract_first,
        "join_values": join_values,
    }

    def __init__(self, schema, field_sep="."):
        self.schema = schema
        self.field_sep = field_sep
        self.fields = self._build_fields()
        self._serialization_methods = dict(self._default_serialization_methods)

    @property
    def fieldnames(self):
        """Field names inferred from schema"""
        return [f.name for f in self.fields]

    def _build_fields(self):
        if self.schema.get("type") != "object":
            raise ValueError("Schema should be of type object")
        return infer_flattened_field_names(self.schema, field_sep=self.field_sep)

    @classmethod
    def from_schemafile(cls, schemafile):
        """Create a Flatson instance from a schemafile"""
        with open(schemafile) as f:
            return cls(json.load(f))

    def _serialize_array_value(self, field, value):
        options = dict(field.serialization_options)

        if options:
            try:
                method = options.pop("method")
            except KeyError:
                raise ValueError(
                    "Missing method in serialization options for field %s" % field.name
                )

            try:
                serialize = self._serialization_methods[method]
            except KeyError:
                raise ValueError(
                    "Unknown serialization method: {method}".format(**options)
                )
            return serialize(value, **options)

        return json.dumps(value, separators=(",", ":"), sort_keys=False)
        # return json.dumps(value, separators=(",", ":"), sort_keys=True)

    def _serialize(self, field, obj):
        value = field.getter(obj)
        if field.is_array():
            return self._serialize_array_value(field, value)
        return value

    def register_serialization_method(self, name, serialize_func):
        """Register a custom serialization method that can be
        used via schema configuration
        """
        if name in self._default_serialization_methods:
            raise ValueError("Can't replace original %s serialization method")
        self._serialization_methods[name] = serialize_func

    def flatten(self, obj):
        """Return a list with the field values"""
        return [self._serialize(f, obj) for f in self.fields]

    def flatten_dict(self, obj):
        """Return an OrderedDict dict preserving order of keys in fieldnames"""
        return OrderedDict(zip(self.fieldnames, self.flatten(obj)))
