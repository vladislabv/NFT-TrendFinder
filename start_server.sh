#!/bin/bash
#source env/bin/activate &&
exec celery -A nft_finder.celery worker -l INFO &
exec python run.py