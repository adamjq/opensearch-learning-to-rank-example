ACTIVE_FEATURES = [
    "title_query",
    "overview_query",
    "title_phrase_query",
    "overview_phrase_query",
    "director_query",
    "genre_query",
    "cast_query",
    "release_date_boost",
    "vote_average_boost",
    "revenue_boost"
]

def get_os_query(query_text: str):
    return {
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
                                "active_features": ACTIVE_FEATURES,
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