import dagster as dg
import clickhouse_connect

class ClickhouseResource(dg.ConfigurableResource):
    host: str
    port: int
    user: str
    pwd: str

    def get_client(self):
        return clickhouse_connect.get_client(
            host= self.host,
            port= self.port,
            username= self.user,
            password= self.pwd,
        )

defs = dg.Definitions(
    resources={
        "clickhouse": ClickhouseResource(
            host = dg.EnvVar("CLICKHOUSE_HOST"),
            port= dg.EnvVar.int("CLICKHOUSE_PORT"),
            user= dg.EnvVar("CLICKHOUSE_USER"),
            pwd= dg.EnvVar("CLICKHOUSE_PASSWORD"),
            # db_name= dg.EnvVar("CLICKHOUSE_DBNAME")
        ),
    }
)