FROM debian:bullseye AS downloader
WORKDIR /app
RUN apt-get update && apt-get install -y wget
ARG GECKODRIVER_VERSION="v0.30.0"
ARG GECKODRIVER_FILENAME="geckodriver-$GECKODRIVER_VERSION-linux64"
RUN wget -q https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/$GECKODRIVER_FILENAME.tar.gz && tar xvf $GECKODRIVER_FILENAME.tar.gz && rm $GECKODRIVER_FILENAME.tar.gz

FROM python:3.10-slim-bullseye as final
RUN apt-get update && apt-get install -y firefox-esr
COPY --from=downloader /app/geckodriver /usr/local/bin/geckodriver
ARG OFX_VERSION
RUN pip install ofx-processor==$OFX_VERSION
CMD ["ynab", "lcl", "--download"]
