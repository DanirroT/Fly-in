

def str_to_dict_parse(in_str: str, entry_sep: str = ",", kv_sep: str = ":",
                      expected_size: int | None = None) -> dict[str, str]:
    out_dict: dict[str, str] = {}

    in_list = in_str.split(entry_sep)

    for entry in in_list:
        entry_split = entry.split(kv_sep)
        if len(entry_split) != 2:
            raise ValueError(f"Error while Parsing a Str to Dict\n{entry}"
                             f" does not have a format <key>{kv_sep}<value>")
        k, v = entry_split

        if out_dict.get(k):
            raise ValueError("Error while Parsing a Str to Dict\nRepeated "
                             f"Keys: {k} goth {out_dict.get(k)} and {v}")
        out_dict[k] = v
    if expected_size and expected_size != len(out_dict):
        raise ValueError(f"Error: expected a size of {expected_size} "
                         f"but got {len(out_dict)}\n{out_dict}")

    return out_dict
