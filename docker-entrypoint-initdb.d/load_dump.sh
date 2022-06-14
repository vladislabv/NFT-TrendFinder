#!/bin/bash
# Update system and install packages
#su root -p pass &&
mongorestore --authenticationDatabase admin -u root -p pass -d nft-finder /dump/nft-finder