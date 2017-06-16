# Base image
FROM python:3.5

MAINTAINER jeremy.pumphrey@nih.gov

ENV INSTALL_PATH /usr/app
RUN mkdir -p "$INSTALL_PATH" && chmod 777 "$INSTALL_PATH"
WORKDIR $INSTALL_PATH

#Install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Add the app code
COPY . .

EXPOSE 5000

# Default command
CMD ["python", "./app.py"]
