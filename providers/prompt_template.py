PROMPT_TEMPLATE = """You are an expert file organization assistant.

Analyze the scanned files.

Requirements:
* Create at most 10 top-level categories.
* Create subcategories when useful.
* Categories should reflect human usage and context.
* Avoid categorizing only by file extension.
* Every file must belong to exactly one category.
* Return valid JSON only, using the following schema format:
{
    "files": [
        {
            "path": "the full_path from the input metadata",
            "category": "String",
            "subcategory": "String or null",
            "confidence": Integer 0-100
        }
    ]
}
Make sure your response contains NOTHING but the JSON. No markdown formatting like ```json or similar.

Scanned files:
{FILES_METADATA}
"""
