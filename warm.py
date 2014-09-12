from osstat.client import StatClient
from osstat.data import prepare_dataframe

client = StatClient()
prepare_dataframe(client)
