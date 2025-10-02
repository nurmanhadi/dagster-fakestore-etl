import dagster as dg

etl_user_schedule = dg.ScheduleDefinition(
    name="etl_user_schedule",
    cron_schedule="* * * * *",
    job_name="etl_user_job",
    execution_timezone="Asia/Jakarta"
)

etl_product_schedule = dg.ScheduleDefinition(
    name="etl_product_schedule",
    cron_schedule="* * * * *",
    job_name="etl_product_job",
    execution_timezone="Asia/Jakarta"
)

etl_cart_schedule = dg.ScheduleDefinition(
    name="etl_cart_schedule",
    cron_schedule="* * * * *",
    job_name="etl_cart_job",
    execution_timezone="Asia/Jakarta"
)