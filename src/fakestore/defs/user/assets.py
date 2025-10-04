import dagster as dg
from dagster import AssetExecutionContext
import requests as req
import pandas as pd
import json

from fakestore.defs.resources import ClickhouseResource

@dg.asset(group_name="user_asset")
def extract_user_from_api(context: AssetExecutionContext) -> list[dict]:
    try:
        response = req.get('https://fakestoreapi.com/users')
        if response.status_code != 200:
            context.log.warning(response.status_code)
        context.log.info("extract user from api success")
        return response.json()
    except Exception as e:
        context.log.error(f"failed extract user from api: {e}")
    return []

@dg.asset(group_name="user_asset", deps=["extract_user_from_api"])
def load_user_json_to_lake(context: AssetExecutionContext, extract_user_from_api: list[dict]) -> None:
    data: list[dict] = extract_user_from_api
    filename: str = "users_raw"
    try:
        with open(f"data/lake/{filename}.json", "w") as file:
            file.write(json.dumps(data))
        context.log.info(f"load {filename} to lake success")
    except Exception as e:
        context.log.error(f"failed load {filename} to lake: {e}")

@dg.asset(group_name="user_asset", deps=["load_user_json_to_lake"])
def transformation_user(context: AssetExecutionContext) -> pd.DataFrame:
    try:
        users: list[dict] = []
        with open('data/lake/users_raw.json', "r") as file:
            data: list[dict] = json.load(file)
            for x in data:
                users.append({
                    "id": x["id"],
                    "email": x["email"],
                    "username": x["username"],
                    "password": x["password"],
                    "name": f"{x['name']['firstname']} {x['name']['lastname']}",
                    "phone": x["phone"],
                    "city": x["address"]["city"],
                    "street": x["address"]["street"],
                    "number": x["address"]["number"],
                    "zipcode": x["address"]["zipcode"],
                })
        df = pd.DataFrame(users)

        # convert data type
        df["id"] = pd.to_numeric(df["id"], errors='coerce').astype("int64")
        df["number"] = pd.to_numeric(df["number"], errors='coerce').astype("int64")
        df["phone"] = df["phone"].str.replace("-", "")
        df["phone"] = pd.to_numeric(df["phone"], errors='coerce').astype("int64")

        # clean text data
        df[["email", "city", "street"]] = df[["email", "city", "street"]].apply(lambda x: x.str.lower())

        # clean data
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)

        context.log.info("transformation user success")
        return df
    except Exception as e:
        context.log.error(f"failed transformation user: {e}")

    return pd.DataFrame([])

@dg.asset(group_name="user_asset", deps=["transformation_user"])
def load_user_to_warehouse(
    context: AssetExecutionContext,
    transformation_user: pd.DataFrame,
    clickhouse: ClickhouseResource) -> None:
    try:
        client = clickhouse.get_client()
        client.insert_df("users", transformation_user)
        context.log.info("load user to warehouse success")
    except Exception as e:
        context.log.error(f"failed load user to warehouse: {e}")