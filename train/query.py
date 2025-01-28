from train.active_features import FEATURES

def get_os_query(query_text: str, model_rescore=False):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query_text,
                            "fields": ["title^3", "overview", "directors", "cast", "genres"]
                        }
                    }
                ],
                "should": [
                    {
                        "sltr": {
                            "featureset": "moviefeatureset",
                            "_name": "logged_featureset",
                            "active_features": FEATURES,
                            "params": {"query_text": query_text},
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        },
        "ext": {
            "ltr_log": {
                "log_specs": {
                    "name": "log_entry1",
                    "named_query": "logged_featureset",
                    "missing_as_zero": True
                }
            }
        }
    }

    if model_rescore:
        query["rescore"] = {
            "window_size": 1000,
            "query": {
                "rescore_query": {
                    "sltr": {
                        "params": {
                            "query_text": query_text
                        },
                        "model": "xgboost_model"
                    }
                }
            }
        }

    return query