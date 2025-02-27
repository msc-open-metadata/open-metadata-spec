import textwrap


class Snowflake:
    def create(
        self,
        name,
        args: list[tuple],
        returns,
        function_definition,
        handler,
        language="PYTHON",
        runtime_version="3.12",
        imports=None,
        packages=None,
        secrets=None,
        external_access_integrations=None,
        or_replace=False,
        temp=False,
        secure=False,
        aggregate=False,
        if_not_exists=False,
        copy_grants=False,
        strict=None,
        volatility=None,
        comment=None,
    ):
        parts = ["CREATE OR ALTER"]

        if or_replace:
            parts.append("OR REPLACE")
        if temp:
            parts.append("TEMPORARY")
        if secure:
            parts.append("SECURE")
        if aggregate:
            parts.append("AGGREGATE")
        if if_not_exists:
            parts.append("IF NOT EXISTS")

        parts.append(f"FUNCTION {name} (")

        args_str = ", ".join(
            f"{arg_name} {arg_type} DEFAULT {default}" if default else f"{arg_name} {arg_type}"
            for arg_name, arg_type, default in args
        )
        parts.append(args_str)
        parts.append(")")

        if copy_grants:
            parts.append("COPY GRANTS")

        parts.append(f"RETURNS {returns}")

        if strict is not None:
            parts.append("STRICT" if strict else "CALLED ON NULL INPUT")

        if volatility:
            parts.append(volatility.upper())

        parts.append(f"LANGUAGE {language}")

        if runtime_version:
            parts.append(f"RUNTIME_VERSION = {runtime_version}")

        if handler:
            parts.append(f"HANDLER = '{handler}'")

        if imports:
            parts.append("IMPORTS = (" + ", ".join(f"'{imp}'" for imp in imports) + ")")

        if packages:
            parts.append("PACKAGES = (" + ", ".join(f"'{pkg}'" for pkg in packages) + ")")

        if external_access_integrations:
            parts.append("EXTERNAL_ACCESS_INTEGRATIONS = (" + ", ".join(external_access_integrations) + ")")

        if secrets:
            parts.append("SECRETS = (" + ", ".join(f"'{key}' = {value}" for key, value in secrets.items()) + ")")

        if comment:
            parts.append(f"COMMENT = '{comment}'")

        parts.append(f"AS \n$$\n{function_definition}\n$$")

        return " ".join(parts) + ";"

    def alter(
        self,
        name,
        args: list[tuple],
        returns,
        function_definition,
        handler,
        language="PYTHON",
        runtime_version="3.12",
        imports=None,
        packages=None,
        secrets=None,
        external_access_integrations=None,
        or_replace=False,
        temp=False,
        secure=False,
        aggregate=False,
        if_not_exists=False,
        copy_grants=False,
        strict=None,
        volatility=None,
        comment=None,
    ):
        """For compatibility: Calls create()"""
        return self.create(
            name,
            args,
            returns,
            function_definition,
            handler,
            language,
            runtime_version,
            imports,
            packages,
            secrets,
            external_access_integrations,
            or_replace,
            temp,
            secure,
            aggregate,
            if_not_exists,
            copy_grants,
            strict,
            volatility,
            comment,
        )

    def drop(self):
        return "Not implemented"


# main
if __name__ == "__main__":
    snowflake = Snowflake()
    snowflake_create_sql = snowflake.create(
        name="my_function",
        args=[("val1", "INT", None), ("val2", "INT", None)],
        returns="INT",
        function_definition=textwrap.dedent("""\
        def add_two_py(val1, val2):
            return val1 + val2
        """),
        handler="add_two_py",
    )

    print(snowflake_create_sql)
