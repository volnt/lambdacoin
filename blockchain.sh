#!/bin/bash
docker run -it -p "127.0.0.1:27017:27017" --rm -v "$PWD/db/:/data/db" mongo
