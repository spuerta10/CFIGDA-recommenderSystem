from os.path import exists, abspath
from joblib import load


class KNNModel:
    def __init__(self, pkl_path: str):
        if not exists(abspath(pkl_path)):
            raise ValueError(f"The path {pkl_path} doesn't exists.")
        
        self._model = load(pkl_path)

    
    def predict(self):
        ...