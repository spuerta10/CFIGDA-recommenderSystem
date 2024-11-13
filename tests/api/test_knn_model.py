from unittest.mock import MagicMock
from api.knn_model import KNNModel
from api.queries.customer_items_array import QUERY as CUSTOMER_ITEMS_ARRAY_QUERY
from api.queries.most_sold_products_for_customer import QUERY as MOST_SOLD_PRODUCTS_FOR_CUSTOMER_QUERY

import pytest
from google.cloud.bigquery import Client
from numpy import array, ndarray
from pandas import DataFrame


@pytest.fixture 
def mock_bq_client() -> MagicMock:
    bq_client = MagicMock(spec=Client)
    return bq_client


@pytest.fixture
def mock_knn_model(mock_bq_client: MagicMock) -> KNNModel:
    return KNNModel(r"src/api/conf/knn_model_conf.json", bq_client=mock_bq_client)


def test_knn_model_init_with_conf_path():
    """Test the initialization of KNNModel with a configuration path.

    This test verifies that KNNModel initializes correctly when provided
    with a configuration file path. It checks that:
    - The configuration (`_conf`) is loaded and is not None.
    - The configuration contains required attributes like `model_pkl_path` and `similar_customers_number`.
    - The model (`_model`) is loaded and is not None.
    - The BigQuery client (`_bq_client`) is an instance of `Client`.
    """
    knn_model =KNNModel(r"src/api/conf/knn_model_conf.json")
    assert knn_model._conf is not None
    assert hasattr(knn_model._conf, "model_pkl_path"), "Missing model_pkl_path in model conf"
    assert hasattr(knn_model._conf, "similar_customers_number"), "Missing similar_customers_number in model conf"
    assert knn_model._model is not None
    assert isinstance(knn_model._bq_client, Client)


def test_knn_model_init_with_custom_bq_client(mock_knn_model: KNNModel, mock_bq_client: MagicMock):
    """Test the initialization of KNNModel with a custom BigQuery client.

    Args:
        mock_knn_model (KNNModel): The KNNModel instance initialized with a mock BigQuery client.
        mock_bq_client (MagicMock): The mock BigQuery client.

    This test checks that when KNNModel is initialized with a custom BigQuery client,
    the client is correctly assigned to the `_bq_client` attribute.
    """
    assert mock_knn_model._bq_client is mock_bq_client
    

def test_query_customer_items_matrix(mock_bq_client: MagicMock, mock_knn_model: KNNModel):
    """Test the _query_customer_items_matrix method for retrieving customer item data.

    Args:
        mock_bq_client (MagicMock): The mock BigQuery client to simulate querying behavior.
        mock_knn_model (KNNModel): The KNNModel instance using the mock BigQuery client.

    This test verifies that the `_query_customer_items_matrix` method:
    - Calls the expected query with the correct `customer_id`.
    - Returns a NumPy array (`ndarray`) representing customer items.
    - Ensures the returned array has the correct shape.
    """
    mock_bq_client.query.return_value.to_dataframe.return_value.to_numpy.return_value = array([[1,2,3]])
    customer_id = 9  # a random customer id just for testing purposes
    result = mock_knn_model._query_customer_items_matrix(customer_id)
    
    mock_bq_client.query.assert_called_once_with(CUSTOMER_ITEMS_ARRAY_QUERY.format(customer_id))
    assert isinstance(result, ndarray)
    assert result.shape == (1, 3)
    

def test_query_recommended_items(mock_bq_client: MagicMock, mock_knn_model: KNNModel):
    """Test the _query_recommended_items method for generating recommendations.

    Args:
        mock_bq_client (MagicMock): The mock BigQuery client to simulate querying behavior.
        mock_knn_model (KNNModel): The KNNModel instance using the mock BigQuery client.

    This test verifies that the `_query_recommended_items` method:
    - Calls the expected query using the given `similar_customers`, `item_ids`, and `num_recommendations`.
    - Returns a list of recommended item IDs.
    """
    mock_bq_client.query.return_value.to_dataframe.return_value = DataFrame({"item_id": [101, 102, 103]})
    similar_customers = [1,2,3]
    item_ids = [10,20]
    num_recommendations = 3
    result = mock_knn_model._query_recommended_items(similar_customers, item_ids, num_recommendations)
    
    mock_bq_client.query.assert_called_once_with(
        MOST_SOLD_PRODUCTS_FOR_CUSTOMER_QUERY.format(
            tuple(similar_customers),
            tuple(item_ids),
            num_recommendations
        )
    )
    assert isinstance(result, list)
    
    
def test_recommend_valid_case(mock_knn_model: KNNModel):
    mock_knn_model\
        ._query_customer_items_matrix = MagicMock(
            return_value = array([[1, 0, 1, 0, 1]])
        )
    mock_knn_model._model.kneighbors = MagicMock(
        return_value = (None, array([[1, 2, 3, 4, 5]])) 
    ) 
    mock_knn_model\
        ._query_recommended_items = MagicMock(
            return_value = [101, 102, 103]
        )
    
    recommendations = mock_knn_model.recommend(
        customer_id= 1,
        order_items=[{"item_id": 26, "item_tags": [30, 19, 2]}, {"item_id": 18, "item_tags": [43, 9]}],
        num_recommendations=3
    )
    
    mock_knn_model._query_customer_items_matrix.assert_called_once_with(1)
    mock_knn_model._model.kneighbors.assert_called_once()
    mock_knn_model \
        ._query_recommended_items \
        .assert_called_once_with(
            [2,3,4,5], [26, 18], 3
        )
    assert recommendations == [101, 102, 103]


def test_recommend_no_order_items(mock_knn_model: KNNModel):
    mock_knn_model\
        ._query_customer_items_matrix = MagicMock(
            return_value = array([[1, 0, 1, 0, 1]])
        )
    mock_knn_model._model.kneighbors = MagicMock(
        return_value = (None, array([[1, 2, 3, 4, 5]])) 
    )
    
    recommendations = mock_knn_model.recommend(
        customer_id= 1,
        order_items=[],
        num_recommendations=3
    )
    assert recommendations == []


def test_invalid_conf_path_raises_error():
    """Test that an invalid configuration path raises a ValueError.

    This test ensures that when KNNModel is initialized with an invalid
    configuration path, a `ValueError` is raised.
    """
    with pytest.raises(ValueError):
        KNNModel(r"src/api/knn_model_conf.json")
