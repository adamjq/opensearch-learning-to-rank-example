# Opnesearch Learning-to-Rank POC

This repo is intended as for educational purposes. It contains the steps needed to get a working implementation of the
[Opensearch Learning to Rank Plugin](https://github.com/o19s/elasticsearch-learning-to-rank) working locally with a dockerized version of Opensearch.

The best way to understand LTR is to [read the official docs here](https://elasticsearch-learning-to-rank.readthedocs.io/en/latest/index.html).

## Requirements
- Docker
- [opensearch-plugin CLI tool](https://opensearch.org/docs/latest/install-and-configure/plugins/)
    - `brew install opensearch`

## 1. Set up Opensearch in Docker

NOTE: To use the OpenSearch image with a custom plugin, you must first create a Dockerfile. See 
- [Working with plugins (Opensearch)](https://opensearch.org/docs/latest/install-and-configure/install-opensearch/docker#working-with-plugins)
- [Installing (LTR official docs)](https://elasticsearch-learning-to-rank.readthedocs.io/en/latest/index.html#installing)

- Opensearch version: `2.5`
- LTR Plugin `v2.1.0` (compatible with OS 2.5). See [plugin release history on GitHub](https://github.com/opensearch-project/opensearch-learning-to-rank-base/releases).

Run:
- `docker compose up`
- `curl http://localhost:9200/_cat/indices` to check the cluster

## 2. Create a movies index with documents

Create an index with an explicit mapping template:
```sh
curl -X PUT "http://localhost:9200/movies" -H 'Content-Type: application/json' -d'
{
    "mappings": {
        "properties": {
            "title": { "type": "text" },
            "description": { "type": "text" },
            "year_released": { "type": "integer" }
        }
    }
}'
```

- `curl http://localhost:9200/movies` to check the index was created successfully

Index a document:
```sh
curl -X POST "http://localhost:9200/_doc" -H 'Content-Type: application/json' -d'
{
    "title": "First Blood",
    "year_released": 1982
}'
```

Search for a movie:
```sh
curl -X GET "http://localhost:9200/_search" -H 'Content-Type: application/json' -d'
{
    "query": {
        "match": {
            "title": "First"
        }
    }
}'
```


## 3. Set up an LTR feature store

Set up default featureset index:
```sh
curl -X PUT "http://localhost:9200/_ltr" -H 'Content-Type: application/json'
```

Create a feature set called `moviefeatureset`:
```sh
curl -X POST "http://localhost:9200/_ltr/_featureset/moviefeatureset" -H 'Content-Type: application/json' -d'
{
   "featureset": {
        "features": [
            {
                "name": "title_query",
                "params": [
                    "query_text"
                ],
                "template_language": "mustache",
                "template": {
                    "match": {
                        "title": "{{query_text}}"
                    }
                }
            },
            {
                "name": "description_query",
                "params": [
                    "query_text"
                ],
                "template_language": "mustache",
                "template": {
                    "match": {
                        "description": "{{query_text}}"
                    }
                }
            }
        ]
   }
}'
```

Run `curl http://localhost:9200/_ltr/_featureset` to see registered features in the featureset.

## 4. Run a query to get logged features

First, run a simple text query:
```sh
curl -X GET "http://localhost:9200/movies/_search" -H 'Content-Type: application/json' -d'
{
    "query": {
        "match": {
            "title": "First"
        }
    }
}'
```

Now, run a query with an SLTR filter to get logged features back:
```sh
curl -X GET "http://localhost:9200/movies/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
      "bool": {
        "filter" : [
            {
                "sltr" : {
                    "featureset" : "moviefeatureset",
                    "_name": "logged_featureset",
                    "active_features" : [ 
                        "title_query",
                        "description_query"
                    ],
                    "params": {
                        "query_text": "First"
                    }
                }
            }
        ]
      }
  },
  "ext": {
        "ltr_log": {
            "log_specs": {
                "name": "log_entry1",
                "named_query": "logged_featureset"
            }
        }
    }
}'
```

Result:
```json
{
  "took": 2,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 1,
      "relation": "eq"
    },
    "max_score": 0.0,
    "hits": [
      {
        "_index": "movies",
        "_id": "rfzam40Bbf4EFOUV1cUr",
        "_score": 0.0,
        "_source": {
          "title": "First Blood",
          "year_released": 1982
        },
        "fields": {
          "_ltrlog": [
            {
              "log_entry1": [
                {
                  "name": "title_query",
                  "value": 0.2876821
                },
                {
                  "name": "description_query"
                }
              ]
            }
          ]
        },
        "matched_queries": [
          "logged_featureset"
        ]
      }
    ]
  }
}
```

Things to note:
- Logged feature values in `"_ltrlog"`
- Feature logging score returned for `title_query`
- Feature log result returned for `description_query` with no score. This is because we originally indexed a document without a description field.
- Nothing at all logged for `year_released`. This is because it was never registered as a feature of interest in the featureset.

## Resources
- [Elasticsearch Learning to Rank: the documentation](https://elasticsearch-learning-to-rank.readthedocs.io/en/latest/index.html)
- [Learning to Rank for Amazon OpenSearch Service (AWS)](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/learning-to-rank.html)
- [Working with plugins (Opensearch)](https://opensearch.org/docs/latest/install-and-configure/install-opensearch/docker#working-with-plugins)
