# Inpsired by https://github.com/o19s/hello-ltr/blob/main/notebooks/opensearch/.docker/opensearch-docker/Dockerfile

FROM opensearchproject/opensearch:2.18.0

# relies on `brew install opensearch`
RUN opensearch-plugin install --batch \
  "https://github.com/opensearch-project/opensearch-learning-to-rank-base/releases/download/v2.18.0/ltr-2.18.0-os2.18.0.zip"
