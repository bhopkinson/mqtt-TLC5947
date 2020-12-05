FROM arm32v7/python:3.8-buster AS base

# Setup virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependancies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Run application
COPY *.py .

CMD ["main.py"]
ENTRYPOINT ["python3"]