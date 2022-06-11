# Pull the latest version of the Python container.
FROM python:3.8-slim-buster
# Pull latest updates for ubuntu and install git
RUN apt-get -y update && apt-get -y install git && apt-get -y install unzip
# Add the everything from git repo to the image.
ADD . /var/NFT-TrendFinder
# Set the working directory to /app/.
WORKDIR /var/NFT-TrendFinder
# Set folder for DALLE
RUN mkdir /var/dalle
# Clone DALLE to already created folder
RUN git clone https://github.com/lucidrains/DALLE-pytorch.git /var/dalle/
# Replace generate.py and place there pretrained model
RUN cp -f ./dalle_monkey_patched/generate.py /var/dalle/generate.py
# Assure that we are able to create virtual environments with python.
RUN pip install virtualenv
# Install package working with Google Drive
RUN pip install gdown
# Download initial images
RUN cd ./image_storage && gdown 1LMEtbhydAXg5CkHtgqn4tiGw8J-HVQTv && unzip nft_finder_temp_images.zip "nft_finder_temp_images/*"
# Clean up
RUN rm ./image_storage/nft_finder_temp_images.zip
# Download pretrained model
RUN cd /var/dalle && gdown 12xOf3Ve7Kzv0Ab8taahCrKEUmBw-qr_j
# Download mongodb dump
RUN cd ./mongodb && gdown 1OuU6Ctqa5HP2EhLGSEf-VFEbCLmixn_9 && unzip mongodb_dump.zip
# Clean up
RUN rm ./mongodb/mongodb_dump.zip
# Set the virtual environment for flask application
RUN virtualenv env -p $(which python3)
# Set the virtual environment for dalle model
RUN virtualenv dalleEnv -p $(which python3)
# Set environment variables for flask application
ENV FLASK_APP=nft_finder
ENV FLASK_ENV=development
# Install Python dependencies for DALLE framework.
ENV PATH="/var/NFT-TrendFinder/dalleEnv/bin:$PATH"
RUN pip install git+https://github.com/lucidrains/DALLE-pytorch.git
# Install Python dependencies.
ENV PATH="/var/NFT-TrendFinder/env/bin:$PATH"
RUN pip install -r requirements.txt && pip install -e .
# Create an unprivileged user for running our Python code.
RUN adduser --disabled-password --gecos 'appRunner' nft_finder
# Start flask server when container is up
ENTRYPOINT ["/var/NFT-TrendFinder/start_server.sh"]