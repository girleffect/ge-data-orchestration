# Stage 1: Build Stage
# FROM python:3.9.11-bullseye as builder
FROM mcr.microsoft.com/azure-cli as builder

ARG ICONV_VERSION="1.16"

COPY requirements.txt .
# RUN apt update && apt install azure-cli
RUN pip install --no-cache -r requirements.txt

# Stage 2: Final Stage
FROM mcr.microsoft.com/azure-cli 

# Copy installed dependencies from the build stage
COPY --from=builder /usr/local /usr/local

COPY log_errors.py .
COPY run.sh .
COPY GE_YT /GE_YT

RUN chmod +x run.sh

CMD ["bash", "-c", "./run.sh 2> >(python ./log_errors.py) | tee"]

