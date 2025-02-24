import json
from collections import defaultdict
from enum import Enum


class MetadataObject(Enum):
    FUNCTION = 1
    USER = 2
    ROLE = 3


class UnionSpec:
    def __init__(
        self,
        obj_name: str,
        *,
        req_args: dict[str, tuple[set[str], str, set[str]]],
        args: dict[str, tuple[set[str], str, set[str]]],
        arg_repeats: defaultdict[str, set[str]],
        fields: dict[str, tuple[set[str], str, set[str]]],
        field_repeats: defaultdict[str, set[str]],
    ):
        self.obj = obj_name
        self.req_args = req_args
        self.args = args
        self.arg_repeats = arg_repeats
        self.fields = fields
        self.field_repeats = field_repeats

    def add_req_arg(self, name: str, type: set[str], doc: str, system: set[str]) -> bool:
        name = name.lower()
        if name in self.req_args:
            self.arg_repeats.setdefault(name, set())
            self.arg_repeats[name].add(self.obj)
            self.req_args[name][0].update(type)
            self.req_args[name][2].update(system)
            return False
        self.req_args[name] = (type, doc, system)
        return True

    def add_arg(self, name: str, type: set[str], doc: str, system: set[str]) -> bool:
        name = name.lower()
        if name in self.args:
            self.arg_repeats.setdefault(name, set())
            self.arg_repeats[name].add(self.obj)
            self.args[name][0].update(type)
            self.args[name][2].update(system)
            return False
        self.args[name] = (type, doc, system)
        return True

    def add_field(self, name: str, type: set[str], doc: str, system: set[str]) -> bool:
        name = name.lower()
        if name in self.fields:
            self.field_repeats.setdefault(name, set())
            self.field_repeats[name].add(self.obj)
            self.fields[name][0].update(type)
            self.fields[name][2].update(system)
            return False
        self.fields[name] = (type, doc, system)
        return True

    def print_req_args(self):
        print(f"Required Args: {len(self.req_args)}")
        for k, v in self.req_args.items():
            print(f"""{k:<25}: {v[1]:>5}
                """)

    def print_args(self):
        print(f"All Args: {len(self.args)}")
        for k, v in self.args.items():
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
        {"All Args":<25}: {len(self.args):>5} ({list(self.args.keys())[:3]}, and {len(self.args) - 3} more)
        {"Fields":<25}: {len(self.fields):>5} ({list(self.fields.keys())[:3]}, and {len(self.fields) - 3} more)
        {"Arg Repeats":<25}: {len(self.arg_repeats):>5} ({list(self.arg_repeats.keys())[:3]}...)
        {"Field Repeats":<25}: {len(self.field_repeats):>5} ({list(self.field_repeats.keys())[:3]}...)
        """

    def export_definition(self, file_path: str) -> None:  # noqa: C901
        serializable_req_args: dict[str, tuple[list[str], str, list[str]]] = {}
        serializable_args: dict[str, tuple[list[str], str, list[str]]] = {}
        serializable_fields: dict[str, tuple[list[str], str, list[str]]] = {}

        for k, v in self.req_args.items():
            serializable_req_args[k] = (list(v[0]), v[1], list(v[2]))

        for k, v in self.args.items():
            serializable_args[k] = (list(v[0]), v[1], list(v[2]))

        for k, v in self.fields.items():
            serializable_fields[k] = (list(v[0]), v[1], list(v[2]))

        with open(file_path, "w+") as f:
            json.dump(
                {
                    "object": self.obj,
                    "required_args": serializable_req_args,
                    "all_args": serializable_args,
                    "fields": serializable_fields,
                },
                f,
                indent=4,
            )

    def sort(self):
        self.req_args = dict(sorted(self.req_args.items()))
        self.args = dict(sorted(self.args.items()))
        self.fields = dict(sorted(self.fields.items()))
        self.arg_repeats = dict(sorted(self.arg_repeats.items()))
        self.field_repeats = dict(sorted(self.field_repeats.items()))

    def apply_heuristic(self, heuristic_path: str):
        remove_req_a: set[str] = set()
        remove_opt_a: set[str] = set()
        remove_fields: set[str] = set()

        with open(heuristic_path) as f:
            heuristic: dict[str, dict] = json.load(f)

        for req_a_name, req_a_val in self.req_args.copy().items():
            for k, v in heuristic.items():
                if req_a_name in v["aliases"]:
                    self.add_req_arg(
                        name=k,
                        type=req_a_val[0] if self.req_args[req_a_name] else req_a_val[0] | self.req_args[req_a_name][0],
                        doc=v["description"],
                        system=req_a_val[2],
                    )
                    self.arg_repeats[req_a_name] = set()
                    remove_req_a.add(req_a_name)
                    break

        for a_name, a_val in self.args.copy().items():
            for k, v in heuristic.items():
                if a_name in v["aliases"]:
                    self.add_arg(
                        name=k,
                        type=a_val[0] if self.args[a_name] else a_val[0] | self.args[a_name][0],
                        doc=v["description"],
                        system=a_val[2],
                    )
                    self.arg_repeats[a_name] = set()
                    remove_opt_a.add(a_name)
                    break

        for field_name, field_val in self.fields.copy().items():
            for k, v in heuristic.items():
                if field_name in v["aliases"]:
                    self.add_field(
                        name=k,
                        type=field_val[0] if self.fields[field_name] else field_val[0] | self.fields[field_name][0],
                        doc=v["description"],
                        system=field_val[2],
                    )
                    self.field_repeats[field_name] = set()
                    remove_fields.add(field_name)
                    break

        [self.req_args.pop(k) for k in remove_req_a if k not in heuristic.keys()]
        [self.args.pop(k) for k in remove_opt_a if k not in heuristic.keys()]
        [self.fields.pop(k) for k in remove_fields if k not in heuristic.keys()]

        self.sort()


def union_spec(obj: MetadataObject, systems: set[str]):
    print("Producing object spec as union over:")
    union_spec = UnionSpec(
        "Function",
        req_args={},
        args={},
        fields={},
        arg_repeats=defaultdict(lambda: set()),
        field_repeats=defaultdict(lambda: set()),
    )

    for s in systems:
        with open(f"objects/{s}.json") as f:
            metadata_object = json.load(f)[f"{obj.name}"]
            fields = metadata_object["fields"]
            args = metadata_object["args"]
            req_args = [a for a in args if "default" not in a]

        print(f"   → {s}.{obj.name}. Required Args: {len(req_args)}. Fields: {len(fields)}")

        for a in args:
            try:
                if "default" not in a:
                    union_spec.add_req_arg(name=a["name"], type=set(a["type"]), doc=a["doc"], system={s})
                union_spec.add_arg(name=a["name"], type=set(a["type"]), doc=a["doc"], system={s})
            except KeyError as e:
                print(f" Error {e} {s}.{obj.name}.{a}. Missing key")
                exit(1)

        for f in fields:
            try:
                union_spec.add_field(name=f["name"], type=set(f["type"]), doc=f["doc"], system={s})
            except KeyError as e:
                print(f" Error {e} {s}.{obj.name}.{f}. Missing key")
                exit(1)

    union_spec.sort()
    return union_spec


# Matching heuristic


if __name__ == "__main__":
    function_systems = {"databricks", "duckdb", "postgres", "unitycatalog", "snowflake"}
    function_spec = union_spec(MetadataObject.FUNCTION, function_systems)

    function_spec.export_definition("spec/function.txt")
    print(function_spec)

    function_spec.apply_heuristic("spec/function_heuristic.json")
    function_spec.export_definition("spec/reduced_function.txt")

    print(function_spec)
