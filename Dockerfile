FROM python:3.8-slim-buster AS base

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
COPY main.py .
COPY mqtt.py .

CMD ["main.py"]
ENTRYPOINT ["python3"]