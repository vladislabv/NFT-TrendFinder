# Pull the latest version of the Python container.
FROM python:3.8-slim-buster
# Pull latest updates for ubuntu and install git
RUN apt-get -y update && apt-get -y install git && apt-get -y install unzip && apt-get -y install wget
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
RUN wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=12xOf3Ve7Kzv0Ab8taahCrKEUmBw-qr_j' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=12xOf3Ve7Kzv0Ab8taahCrKEUmBw-qr_j" -O /var/dalle/dalle.pt && rm -rf /tmp/cookies.txt
# Set the virtual environment for flask application
# RUN python3 -m venv /var/NFT-TrendFinder/env
# Set the virtual environment for dalle model
# RUN python3 -m venv /var/NFT-TrendFinder/dalleEnv
# Install Python dependencies for DALLE framework.
# ENV PATH="/var/NFT-TrendFinder/dalleEnv/bin:$PATH"
RUN pip install git+https://github.com/lucidrains/DALLE-pytorch.git
# Set environment variables for flask application
ENV FLASK_APP=nft_finder
ENV FLASK_ENV=development
# Install Python dependencies.
# ENV PATH="/var/NFT-TrendFinder/env/bin:$PATH"
RUN pip install -r requirements.txt && pip install -e .
# Create an unprivileged user for running our Python code.
RUN adduser --disabled-password --gecos 'appRunner' nft_finder
# Start flask server when container is up
ENTRYPOINT ["/var/NFT-TrendFinder/start_server.sh"]
#CMD . /env/bin/activate && /var/NFT-TrendFinder/start_server.sh
#RUN ["/bin/bash", "-c", "source /var/NFT-TrendFinder/env/bin/activate && /var/NFT-TrendFinder/start_server.sh"]
