from typing import Callable

def clean_prompts(
        raw_data : list[dict[str, str | None]],
        cleaner_func : Callable[[str], str]
) -> list[str]:
    results: list[str] = []
    for raw in raw_data:
        if raw["prompt"] is not None:
            cleaned = cleaner_func(raw["prompt"])
            results.append(cleaned)
    return results

def toLower(text : str) -> str:
    return text.lower()

def main() -> None:
    processed = clean_prompts([{"prompt": "You are GOOD"}, {"prompt": ""}], toLower)
    print(processed)

if __name__ == "__main__":
    main()



# # 1. str | None is exactly like returning Optional<String>
# def fetch_database_record(record_id: int) -> dict[str, str] | None:
#     mock_db = {1: {"content": "Hello AI"}, 2: {"content": "Strict typing is great"}}
#     return mock_db.get(record_id)
#
#
# # 2. Callable[[input_types], return_type] acts like a Java functional interface
# def process_records(
#         record_ids: list[int],
#         formatter: Callable[[str], str]
# ) -> list[str]:
#     results: list[str] = []
#
#     for rid in record_ids:
#         record = fetch_database_record(rid)
#
#         # Pyright will throw an error if you forget this null check!
#         if record is not None:
#             # We know 'record' is a dict, and 'content' is a string
#             formatted_text = formatter(record["content"])
#             results.append(formatted_text)
#
#     return results


# def to_uppercase(text: str) -> str:
#     return text.upper()
#
#
# def main() -> None:
#     # Passing the function as a Callable, just like passing a lambda or method reference in Java
#     processed = process_records([1, 2, 99], to_uppercase)
#     print(processed)
#
#
# if __name__ == "__main__":
#     main()