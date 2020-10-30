FROM python:latest

# Install python and pip
ADD ./requirements.txt /tmp/requirements.txt

# Install dependencies
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt --use-feature=2020-resolver

# Add our code
ADD . /opt/webapp/
WORKDIR /opt/webapp

# Expose is NOT supported by Heroku
# EXPOSE 5000

# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku
CMD adev runserver aiohttp_admin2/demo/__init__.py --port=$PORT
