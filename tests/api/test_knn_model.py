from unittest.mock import MagicMock
from src.api.knn_model import KNNModel

import pytest
from google.cloud.bigquery import Client


@pytest.fixture 
def mock_bq_client() -> MagicMock:
    bq_client = MagicMock(spec=Client)
    return bq_client


@pytest.fixture
def mock_knn_model(mock_bq_client: MagicMock) -> KNNModel:
    return KNNModel(r"src/api/conf/knn_model_conf.json", bq_client= mock_bq_client)


def test_knn_model_init_with_conf_path():
    knn_model =KNNModel(r"src/api/conf/knn_model_conf.json")
    assert knn_model._conf is not None
    assert hasattr(knn_model._conf, "model_pkl_path"), "Missing model_pkl_path in model conf"
    assert hasattr(knn_model._conf, "similar_customers_number"), "Missing similar_customers_number in model conf"
    assert knn_model._model is not None
    assert isinstance(knn_model._bq_client, Client)


def test_knn_model_init_with_custom_bq_client(mock_knn_model: KNNModel, mock_bq_client: MagicMock):
    assert mock_knn_model._bq_client is mock_bq_client



