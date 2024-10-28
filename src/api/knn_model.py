from joblib import load
from api.queries.customer_items_array import QUERY as CUSTOMER_ITEMS_ARRAY_QUERY
from api.queries.most_sold_products_for_customer import QUERY as MOST_SOLD_PRODUCTS_FOR_CUSTOMER_QUERY

from google.cloud.bigquery import Client
from credit_risk_lib.config.config import Config
from credit_risk_lib.config.config_factory import ConfigFactory
from sklearn.neighbors import NearestNeighbors
from numpy import ndarray
from pandas import DataFrame


class KNNModel:
    def __init__(
        self, 
        knn_model_conf_path: str,
        bq_client: Client = None
    ):
        self._conf: Config = ConfigFactory.get_conf(knn_model_conf_path)
        self._model: NearestNeighbors = load(self._conf.model_pkl_path)
        self._bq_client = Client() if bq_client is None else bq_client
        
    
    def _query_customer_items_matrix(self, customer_id: int) -> ndarray:
        """
        Retrieves the items purchased by a specific customer and returns them 
        as a NumPy array.

        Args:
            customer_id (int): The unique identifier of the customer whose 
            purchased items are being queried.

        Returns:
            ndarray: A NumPy array representing the items purchased by the 
            specified customer, reshaped into a single row.
        """
        return (
            self._bq_client
            .query(CUSTOMER_ITEMS_ARRAY_QUERY.format(customer_id))
            .to_dataframe()
            .to_numpy()
            .reshape(1,-1) 
        )
    
    
    def _query_recommended_items(
        self,
        similar_customers: list,
        item_ids: list,
        num_recommendations: int
    ) -> list[int]:
        """
        Queries the recommended items based on similar customers and given 
        item IDs, returning a list of recommended item IDs.

        Args:
            similar_customers (list): A list of customer IDs that are similar 
            to the target customer.
            item_ids (list): A list of item IDs that the target customer has 
            interacted with.
            num_recommendations (int): The number of recommended items to 
            return.

        Returns:
            list[int]: A list of item IDs recommended for the target customer.
        """
        recommended_items_df: DataFrame = (
            self._bq_client
            .query(MOST_SOLD_PRODUCTS_FOR_CUSTOMER_QUERY.format(
                tuple(similar_customers),
                tuple(item_ids),
                num_recommendations
            ))
            .to_dataframe() 
        )
        return recommended_items_df["item_id"].tolist()
    
    
    def recommend(
        self,
        customer_id: int,
        order_items: list[dict],
        num_recommendations: int = 3
    ) -> list[int]:
        """
        Recommended items for a given customer based on their past 
        purchases and the purchases of similar customers.

        Args:
            customer_id (int): The unique identifier of the customer for whom 
            recommendations are being predicted.
            order_items (list[dict]): A list of dictionaries containing the 
            details of the items that the customer is interested in.
            num_recommendations (int, optional): The number of recommendations 
            to return. Defaults to 3.

        Returns:
            list[int]: A list of recommended item IDs for the specified 
            customer.
        """
        customer_items_matrix: ndarray = self._query_customer_items_matrix(customer_id)
        _, similar_customers = self._model.kneighbors(
            customer_items_matrix, 
            n_neighbors= self._conf.similar_customers_number
        )
        similar_customers: list[int] = similar_customers \
            .flatten().tolist()  # pass from numpy ndarray to python list
        similar_customers: list[int] = similar_customers[1:]  # The first position is always the given customer id
        item_ids: list[int] = [item["item_id"] for item in order_items]
        # TODO: See what happens if there are not similar customers
        recommended_items = self._query_recommended_items(similar_customers, item_ids, num_recommendations)
        return recommended_items
        
        