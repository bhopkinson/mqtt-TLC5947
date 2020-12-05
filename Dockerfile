FROM arm32v7/python:3.8-slim-buster AS base

RUN apt-get update
RUN apt-get install gcc python-dev

# Setup virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependancies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Use non-root user
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

# Run application
COPY *.py .

CMD ["main.py"]
ENTRYPOINT ["python3"]