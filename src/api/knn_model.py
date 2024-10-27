from joblib import load
from api.queries.customer_items_array import QUERY as CUSTOMER_ITEMS_ARRAY_QUERY

from google.cloud.bigquery import Client
from credit_risk_lib.config.config import Config
from credit_risk_lib.config.config_factory import ConfigFactory 


class KNNModel:
    def __init__(
        self, 
        knn_model_conf_path: str,
        bq_client: Client = None
    ):
        self._conf: Config = ConfigFactory.get_conf(knn_model_conf_path)
        self._bq_client = Client() if bq_client is None else bq_client
        
    
    def predict(
        self,
        customer_id: int,
        order_items: list,
        num_recommendations: int = 3
    ):
        model = load(self._conf.model_pkl_path)
        customer_items_array = self._bq_client.query(CUSTOMER_ITEMS_ARRAY_QUERY)
        