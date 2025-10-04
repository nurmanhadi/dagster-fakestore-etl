import dagster as dg
from dagster import AssetExecutionContext
import requests as req
import pandas as pd
import json

from fakestore.defs.resources import ClickhouseResource

@dg.asset(group_name="product_asset")
def extrack_product_from_api(context: AssetExecutionContext) -> list[dict]:
    try:
        response = req.get('https://fakestoreapi.com/products')
        if response.status_code != 200:
            context.log.warning(response.status_code)
        context.log.info("extract products from api success")
        return response.json()
    except Exception as e:
        context.log.error(f"failed extract product from api: {e}")
    return []

@dg.asset(group_name="product_asset", deps=["extrack_product_from_api"])
def load_product_json_to_lake(context: AssetExecutionContext, extrack_product_from_api: list[dict]) -> None:
    data: list[dict] = extrack_product_from_api
    filename: str = "products_raw"
    try:
        with open(f"data/lake/{filename}.json", "w") as file:
            file.write(json.dumps(data))
        context.log.info(f"load {filename} to lake success")
    except Exception as e:
        context.log.error(f"failed load {filename} to lake: {e}")

@dg.asset(group_name="product_asset", deps=["load_product_json_to_lake"])
def transformation_product(context: AssetExecutionContext) -> pd.DataFrame:
    try:
        idr: float = 16759
        products: list[dict] = []
        with open('data/lake/products_raw.json', "r") as file:
            data: list[dict] = json.load(file)
            for x in data:
                products.append({
                    "id": x["id"],
                    "title": x["title"],
                    "price_usd": x["price"],
                    "description": x["description"],
                    "category": x["category"],
                    "image": x["image"],
                    "rate": x["rating"]["rate"],
                    "count": x["rating"]["count"]
                })
            
        df = pd.DataFrame(products)

        # convert data type
        df["id"] = pd.to_numeric(df["id"], errors='coerce').astype("int64")
        df["price_usd"] = pd.to_numeric(df["price_usd"], errors='coerce').astype("float64")
        df["rate"] = pd.to_numeric(df["rate"], errors='coerce').astype("float64")
        df["count"] = pd.to_numeric(df["count"], errors='coerce').astype("int64")

        # add column price_idr
        df["price_idr"] = idr * df["price_usd"].astype("float64")

        # clean text data
        df[["title", "description", "category"]] = df[["title", "description", "category"]].apply(lambda x: x.str.strip().str.lower())

        # clean data
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)
        context.log.info("transformation product success")
        return df
    except Exception as e:
        context.log.error(f"failed transformation product: {e}")

    return pd.DataFrame([])

@dg.asset(group_name="product_asset", deps=["transformation_product"])
def load_product_to_warehouse(
    context: AssetExecutionContext,
    transformation_product: pd.DataFrame,
    clickhouse: ClickhouseResource) -> None:
    try:
        client = clickhouse.get_client()
        client.insert_df("products", transformation_product)
        context.log.info("load product to warehouse success")
    except Exception as e:
        context.log.error(f"failed load product to warehouse: {e}")