import wrds

db = wrds.Connection()

cols = db.describe_table(
    library="comp_global_daily",
    table="g_funda"
)

print(cols[["name", "type"]].to_string())