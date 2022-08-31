#!/bin/bash
#source env/bin/activate &&
exec python -m pytest /var/NFT-TrendFinder/testing &&
exec celery -A nft_finder.celery worker -l INFO &
exec python run.py