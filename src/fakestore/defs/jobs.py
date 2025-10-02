import dagster as dg

etl_user_job = dg.define_asset_job(
    name="etl_user_job",
    selection= dg.AssetSelection.groups("user_asset")
    )

etl_product_job = dg.define_asset_job(
    name="etl_product_job",
    selection= dg.AssetSelection.groups("product_asset")
)

etl_cart_job = dg.define_asset_job(
    name="etl_cart_job",
    selection= dg.AssetSelection.groups("cart_asset")
)