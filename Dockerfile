FROM debian:bookworm AS downloader
WORKDIR /app
RUN apt-get update && apt-get install -y wget
ARG GECKODRIVER_VERSION="v0.33.0"
ARG GECKODRIVER_FILENAME="geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz"
RUN wget -q https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/$GECKODRIVER_FILENAME \
    && tar xvf $GECKODRIVER_FILENAME  \
    && rm $GECKODRIVER_FILENAME

FROM python:3.11-slim-bookworm as final
RUN apt-get update && apt-get install -y firefox-esr
COPY --from=downloader /app/geckodriver /usr/local/bin/geckodriver
ARG OFX_VERSION
RUN pip --disable-pip-version-check install --quiet ofx-processor==$OFX_VERSION
CMD ["ynab", "lcl", "--download"]
