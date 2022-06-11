#!/bin/bash

exec celery -A nft_finder.celery worker -l INFO &
exec python run.py