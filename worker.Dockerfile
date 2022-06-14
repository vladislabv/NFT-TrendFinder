# Pull the latest version of the Python container.
FROM python:3.8-slim-buster

# copy contents of project into docker
COPY . /var/NFT-TrendFinder

# We will use internal functions of the API
# So install all dependencies of the API
RUN cd /var/NFT-TrendFinder && pip install -r requirements.txt

WORKDIR /var/NFT-TrendFinder

ENV FLASK_APP=nft_finder
ENV FLASK_ENV=development

RUN pip install -e .