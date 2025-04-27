import uuid
import pandas as pd


def convert_structured_result_to_df(structured_result):
    if not isinstance(structured_result, dict):
        json_data = structured_result.model_dump()
    else:
        json_data = structured_result

    rows = []
    meal_id = str(uuid.uuid4())

    for ingredient in json_data["ingredients"]:
        rows.append(
            {
                "meal_id": meal_id,
                "title": json_data["title"],
                "ingredient_name": ingredient["name"],
                "ingredient_amount": ingredient["amount"],
            }
        )

    # Create DataFrame
    df = pd.DataFrame(rows)
    return df
