import re

newline_after_comma_regex = re.compile(r",\W*\n", re.UNICODE)
comma_regex = re.compile(r"}\s*,*\s*{", re.UNICODE)
additional_newline_regex = re.compile(r"\n\n+", re.UNICODE)
def jsonl_to_keyed(jsonl_file: str, key: str) -> str:
    """Converts a JSONL file to a string with a dictionary keyed by the specified key."""
    jsonl_file = jsonl_file.strip().strip("[]").replace("\n", "")
    jsonl_file = newline_after_comma_regex.sub(",", jsonl_file)
    jsonl_file = comma_regex.sub("}\n{", jsonl_file)
    jsonl_file = additional_newline_regex.sub("\n", jsonl_file)
    return f"{{\"{key}\": [{','.join(jsonl_file.splitlines())}]}}"