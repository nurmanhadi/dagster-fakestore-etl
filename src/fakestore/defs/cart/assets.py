import dagster as dg
from dagster import AssetExecutionContext
import requests as req
import pandas as pd
import json

@dg.asset(group_name="cart_asset")
def extract_cart_from_api(context: AssetExecutionContext) -> list[dict]:
    try:
        response = req.get('https://fakestoreapi.com/carts')
        if response.status_code != 200:
            context.log.warning(response.status_code)
        context.log.info("extract carts from api success")
        return response.json()
    except Exception as e:
        context.log.error(f"failed extract cart from api: {e}")
    return []

@dg.asset(group_name="cart_asset", deps=["extract_cart_from_api"])
def load_cart_json_to_lake(context: AssetExecutionContext, extract_cart_from_api: list[dict]) -> None:
    data: list[dict] = extract_cart_from_api
    filename: str = "carts_raw"
    try:
        with open(f"data/lake/{filename}.json", "w") as file:
            file.write(json.dumps(data))
        context.log.info(f"load {filename} to lake success")
    except Exception as e:
        context.log.error(f"failed load {filename} to lake: {e}")

@dg.asset(group_name="cart_asset", deps=["load_cart_json_to_lake"])
def transformation_cart(context: AssetExecutionContext) -> pd.DataFrame:
    try:
        carts: list[dict] = []
        with open('data/lake/carts_raw.json', "r") as file:
            data: list[dict] = json.load(file)
            for x in data:
                for y in x["products"]:
                    carts.append({
                        "id": x["id"],
                        "user_id": x["userId"],
                        "product_id": y["productId"],
                        "quantity": y["quantity"],
                        "date": x["date"]
                    })
        
        df = pd.DataFrame(carts)

        # convert type data
        df["id"] = pd.to_numeric(df["id"], errors='coerce')
        df["user_id"] = pd.to_numeric(df["user_id"], errors='coerce')
        df["product_id"] = pd.to_numeric(df["product_id"], errors='coerce')
        df["quantity"] = pd.to_numeric(df["quantity"], errors='coerce')
        df["date"] = pd.to_datetime(df["date"], format="mixed")

        # clean data
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)

        context.log.info("transform carts success")
        return df
    except Exception as e:
        context.log.error(f"failed transform carts: {e}")

    return pd.DataFrame([])

@dg.asset(group_name="cart_asset", deps=["transformation_cart"])
def load_cart_parquet_to_warehouse(context: AssetExecutionContext, transformation_cart: pd.DataFrame) -> None:
    data: pd.DataFrame = transformation_cart
    filename: str = "products_clean"
    try:
        data.to_parquet(f"data/warehouse/{filename}.parquet", index=False)
        context.log.info(f"load {filename} to warehouse success")
    except Exception as e:
        context.log.error(f"failed load {filename} to warehouse: {e}")