# Opnesearch Learning-to-Rank POC

This repo is intended as for educational purposes. It contains the steps needed to get a working implementation of the
[Opensearch Learning to Rank Plugin](https://github.com/o19s/elasticsearch-learning-to-rank) working locally with a dockerized version of Opensearch.

The best way to understand LTR is to [read the official docs here](https://elasticsearch-learning-to-rank.readthedocs.io/en/latest/index.html).

## Install

Project install:
```sh
pyenv local 3.12
poetry env use 3.12
poetry install
```


## Requirements
- Docker
- [opensearch-plugin CLI tool](https://opensearch.org/docs/latest/install-and-configure/plugins/)
    - `brew install opensearch`

## 1. Set up Opensearch in Docker

NOTE: To use the OpenSearch image with a custom plugin, you must first create a Dockerfile. See 
- [Working with plugins (Opensearch)](https://opensearch.org/docs/latest/install-and-configure/install-opensearch/docker#working-with-plugins)
- [Installing (LTR official docs)](https://elasticsearch-learning-to-rank.readthedocs.io/en/latest/index.html#installing)

- Opensearch version: `2.18.0`
- LTR Plugin `v2.18.0` (compatible with OS 2.15.0). See [plugin release history on GitHub](https://github.com/opensearch-project/opensearch-learning-to-rank-base/releases).

Run:
- `docker compose up`
- `curl http://localhost:9200` in a new terminal to check the cluster

## 2. Create index mapping and bulk index data

```sh
./bin/index.sh
```

Search for a movie to confirm it worked:

```sh
curl -X GET "http://localhost:9200/tmdb/_search?pretty=true" -H 'Content-Type: application/json' -d'
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
curl -X PUT "http://localhost:9200/_ltr?pretty=true" -H 'Content-Type: application/json'
```

Create a feature set called `moviefeatureset`:
```sh
curl -X PUT "http://localhost:9200/_ltr/_featureset/moviefeatureset?pretty=true" -H 'Content-Type: application/json' -d '@featureset.json'
```

Run `curl http://localhost:9200/_ltr/_featureset?pretty=true` to see registered features in the featureset.

## 4. Run a query to get logged features

First, run a python script to generate an example query with SLTR feature logging:
```py
python save_query.py "First Blood"
```

Then, run the query:
```sh
curl -X GET "http://localhost:9200/tmdb/_search?pretty=true" \
  -H 'Content-Type: application/json' \
  -d @example-ltr.json
```

Run the feature logging job:

```sh
poetry shell
python train/log_features.py
```

Things to note:
- Logged feature values in `"_ltrlog"`
- Feature logging score returned for `title_query`
- Feature log result returned for `overview_query` with no score. This is because we originally indexed a document without a description field.
- Nothing at all logged for `year_released`. This is because it was never registered as a feature of interest in the featureset.

## 5. Train an XGBoost model

```sh
poetry shell
python train/train.py
```

Inspect the model at `train/model/model.json`.

## 6. Upload the model to Opensearch

```sh
curl -X POST "http://localhost:9200/_ltr/_featureset/moviefeatureset/_createmodel" \
  -H 'Content-Type: application/json' \
  -d @train/model/os_model.json
```

## 7. Run a query with the model

```sh
poetry shell
python save_query.py "First Blood" --rescore
```

Then, run the query:
```sh
curl -X GET "http://localhost:9200/tmdb/_search?pretty=true" \
  -H 'Content-Type: application/json' \
  -d @example-ltr-rescore.json
```

## Resources
- [Elasticsearch Learning to Rank: the documentation](https://elasticsearch-learning-to-rank.readthedocs.io/en/latest/index.html)
- [Learning to Rank for Amazon OpenSearch Service (AWS)](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/learning-to-rank.html)
- [Working with plugins (Opensearch)](https://opensearch.org/docs/latest/install-and-configure/install-opensearch/docker#working-with-plugins)
- [Example LTR judgement list for movies](https://github.com/o19s/elasticsearch-ltr-demo/blob/master/train/movie_judgments.txt)

