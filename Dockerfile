# Base image
FROM python:3.6

MAINTAINER jeremy.pumphrey@nih.gov

ENV INSTALL_PATH /usr/app
ARG NEW_RELIC_KEY
RUN mkdir -p "$INSTALL_PATH" && chmod 777 "$INSTALL_PATH"
WORKDIR $INSTALL_PATH

#Install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Add the app code
COPY . .
RUN sed -i.bak "s/license_key =/license_key = ${NEW_RELIC_KEY}/g" /usr/app/custom-newrelic.ini

EXPOSE 5000

# Default command
#CMD ["python", "./app.py"]
ENTRYPOINT ["./run_script.sh"]
