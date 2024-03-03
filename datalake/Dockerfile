# Stage 1: Build Stage
# FROM --platform=linux/amd64 python:3.11.6-bullseye as builder
FROM --platform=linux/amd64 mcr.microsoft.com/azure-cli as builder
WORKDIR /
ARG ICONV_VERSION="1.16"

COPY requirements.txt .

RUN pip install --no-cache -r requirements.txt

# Stage 2: Final Stage
FROM --platform=linux/amd64 mcr.microsoft.com/azure-cli 
# FROM --platform=linux/amd64 python:3.11.6-bullseye

# Copy installed dependencies from the build stage
COPY --from=builder /usr/local /usr/local

COPY log_errors.py .
COPY run.sh .
COPY GE_YT /GE_YT
COPY utils /utils
COPY *.py .

RUN chmod +x run.sh

CMD ["bash", "-c", "./run.sh 2> >(python ./log_errors.py) | tee"]
