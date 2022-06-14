# Pull the latest version of the Python container.
FROM mongo:latest

RUN apt-get -y update && apt-get -y install unzip && apt-get -y install wget
RUN mkdir dump
# Download mongodb dump
RUN wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1OuU6Ctqa5HP2EhLGSEf-VFEbCLmixn_9' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1OuU6Ctqa5HP2EhLGSEf-VFEbCLmixn_9" -O /dump/mongodb_dump.zip
RUN unzip /dump/mongodb_dump.zip "dump/*"
# Clean up
RUN rm -rf /tmp/cookies.txt
RUN rm /dump/mongodb_dump.zip
