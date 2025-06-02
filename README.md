# open-metadata-spec

This is an early brainstorming and proof of concept that repository was developed at ITU as part of a the Master thesis: _OpenDict: An Approach to Open Management of All Metadata Objects_.

**Authors**: Andreas Kongstad & Carl Bruun

**Purpose**: This was used for early brainstorming in creating a universally compatible metadata object specification. The approach was later abandoned for a user-centric approach.

## Examples

```json
{
    "object": "Function",
    "required_args": {
        "arg_data_type": [
            [
                "string"
            ],
            "Use the Snowflake data type that corresponds to the handler language that you are using",
            [
                "snowflake"
            ]
        ],
        "function_definition": [
            [
                "string"
            ],
            "(AS) Defines the handler code executed when the UDF is called. The function_definition value must be source code in one of the languages supported for handlers (or SQL).",
            [
                "snowflake",
                "duckdb"
            ]
        ],
        "function_name": [
            [
                "string"
            ],
            "Specifies the name of the function, optionally including schema and catalog.",
            [
                "snowflake",
                "duckdb"
            ]
        ],
        ...  
   }
}
```
