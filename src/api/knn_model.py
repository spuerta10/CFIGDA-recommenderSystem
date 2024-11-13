"""
Module for generating personalized item recommendations for customers 
based on past purchase data and similarity to other customers.
"""

from typing import List

from google.cloud.bigquery import Client
from credit_risk_lib.config.config import Config
from credit_risk_lib.config.config_factory import ConfigFactory
from sklearn.neighbors import NearestNeighbors
from numpy import ndarray
from pandas import DataFrame

from joblib import load
from api.queries.customer_items_array import QUERY as CUSTOMER_ITEMS_ARRAY_QUERY
from api.queries.most_sold_products_for_customer import (
    QUERY as MOST_SOLD_PRODUCTS_FOR_CUSTOMER_QUERY,
)  # pylint: disable=line-too-long


class KNNModel:
    """
    A K-Nearest Neighbors (KNN) model class for generating personalized
    item recommendations for customers based on past purchase data and
    similarity to other customers.

    This class allows querying a customer's purchase data from BigQuery,
    finding similar customers using a pre-trained KNN model, and retrieving
    recommended items.

    Attributes:
        _conf (Config): Configuration object containing model parameters
        such as paths and settings for the number of similar customers.
        _model (NearestNeighbors): Pre-trained NearestNeighbors model for
        finding similar customers.
        _bq_client (Client): BigQuery client used for querying customer data.
    """

    def __init__(self, knn_model_conf_path: str, bq_client: Client = None):
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
            self._bq_client.query(CUSTOMER_ITEMS_ARRAY_QUERY.format(customer_id))
            .to_dataframe()
            .to_numpy()
            .reshape(1, -1)
        )

    def _query_recommended_items(
        self, similar_customers: List, item_ids: List, num_recommendations: int
    ) -> List[int]:
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
        if not similar_customers or not item_ids:
            return []
        
        recommended_items_df: DataFrame = self._bq_client.query(
            MOST_SOLD_PRODUCTS_FOR_CUSTOMER_QUERY.format(
                tuple(similar_customers), tuple(item_ids), num_recommendations
            )
        ).to_dataframe()
        return recommended_items_df["item_id"].tolist()

    def recommend(
        self, customer_id: int, order_items: List[dict], num_recommendations: int = 3
    ) -> List[int]:
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
            customer_items_matrix, n_neighbors=self._conf.similar_customers_number
        )
        similar_customers: List[int] = (
            similar_customers.flatten().tolist()
        )  # pass from numpy ndarray to python list
        similar_customers: List[int] = similar_customers[
            1:
        ]  # The first position is always the given customer id
        item_ids: List[int] = [item["item_id"] for item in order_items]
        # TODO: See what happens if there are not similar customers
        recommended_items = self._query_recommended_items(
            similar_customers, item_ids, num_recommendations
        )
        return recommended_items
