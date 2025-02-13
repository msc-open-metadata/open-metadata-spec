import json
from collections import defaultdict
from enum import Enum


class MetadataObject(Enum):
    FUNCTION = 1
    USER = 2


class UnionSpec:
    def __init__(
        self,
        obj: str,
        *,
        req_args: dict[str, tuple[list, str]],
        opt_args: dict[str, tuple[list, str]],
        arg_repeats: defaultdict[str, set] = defaultdict(set),
        fields: dict[str, tuple[list, str]],
        field_repeats: defaultdict[str, set] = defaultdict(set),
    ):
        self.obj = obj
        self.req_args = req_args
        self.opt_args = opt_args
        self.arg_repeats = arg_repeats
        self.fields = fields
        self.field_repeats = field_repeats

    def print_req_args(self):
        print(f"Required Args: {len(self.req_args)}")
        for k, v in self.req_args.items():
            print(f"""{k:<25}: {v[1]:>5}
                """)

    def print_opt_args(self):
        print(f"Optional Args: {len(self.opt_args)}")
        for k, v in self.opt_args.items():
            print(f"""{k:<25}: {v[1]:>5}
                """)

    def print_fields(self):
        print(f"Fields: {len(self.fields)}")
        for k, v in self.fields.items():
            print(f"""{k:<25}: {v[1]:>5}
                """)

    def print_repeats(self):
        print(f"Arg Repeats: {len(self.arg_repeats)}")
        for k, v in self.arg_repeats.items():
            print(f"""{k:<25}: {v:>5}
                """)

        print(f"Field Repeats: {len(self.field_repeats)}")
        for k, v in self.field_repeats.items():
            print(f"""{k:<25}: {v:>5}
                """)

    def __str__(self):
        return f"""UnionSpec {self.obj}:
        {"Required Args":<25}: {len(self.req_args):>5} ({list(self.req_args.keys())[:3]}, and {len(self.req_args) - 3} more)
        {"Optional Args":<25}: {len(self.opt_args):>5} ({list(self.opt_args.keys())[:3]}, and {len(self.opt_args) - 3} more)
        {"Fields":<25}: {len(self.fields):>5} ({list(self.fields.keys())[:3]}, and {len(self.fields) - 3} more)
        {"Arg Repeats":<25}: {len(self.arg_repeats):>5} ({list(self.arg_repeats.keys())[:3]}...)
        {"Field Repeats":<25}: {len(self.field_repeats):>5} ({list(self.field_repeats.keys())[:3]}...)
        """

    def sort(self):
        self.req_args = dict(sorted(self.req_args.items()))
        self.opt_args = dict(sorted(self.opt_args.items()))
        self.fields = dict(sorted(self.fields.items()))
        self.arg_repeats = dict(sorted(self.arg_repeats.items()))
        self.field_repeats = dict(sorted(self.field_repeats.items()))


def union_spec(obj: MetadataObject, systems: set[str]):
    print("Producing object spec as union over:")
    union_spec = UnionSpec("Function", req_args=dict(), opt_args=dict(), fields=dict())

    for s in systems:
        with open(f"objects/{s}.json") as f:
            metadata_object = json.load(f)[f"{obj.name}"]

        fields = metadata_object["fields"]
        args = metadata_object["args"]
        req_args = [a for a in args if "default" not in a]

        print(
            f"   → {s}.{obj.name}. Required Args: {len(req_args)}. Fields: {len(fields)}"
        )
        for a in req_args:
            try:
                union_spec.req_args[a["name"]] = (a["type"], a["doc"])
            except KeyError:
                union_spec.arg_repeats[a["name"]].add(s)
        for a in args:
            try:
                if "default" in a:
                    union_spec.opt_args[a["name"]] = (a["type"], a["doc"])
            except KeyError:
                union_spec.arg_repeats[a["name"]].add(s)

        for f in fields:
            try:
                union_spec.fields[f["name"]] = (f["type"], f["doc"])
            except KeyError:
                union_spec.field_repeats[f["name"]].add(s)

    union_spec.sort()

    return union_spec


if __name__ == "__main__":
    function_systems = {"databricks", "duckdb", "postgres", "unitycatalog", "snowflake"}
    function_spec = union_spec(MetadataObject.FUNCTION, function_systems)

    function_spec.print_req_args()

    function_spec.print_opt_args()

    function_spec.print_fields()

    print(function_spec)
