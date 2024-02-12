# Inpsired by https://github.com/o19s/hello-ltr/blob/main/notebooks/opensearch/.docker/opensearch-docker/Dockerfile

FROM opensearchproject/opensearch:2.5.0

# relies on `brew install opensearch`
RUN opensearch-plugin install --batch \
  "https://www.github.com/opensearch-project/opensearch-learning-to-rank-base/releases/download/release-v2.1.0/ltr-plugin-v2.1.0.zip"
