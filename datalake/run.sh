#!/usr/bin/env bash

# This script is used to run data pipeline scripts based on the value of the SOURCE variable.
# It handles error handling, downloads secrets files, and executes the data pipeline script accordingly.

error_handler() {
  echo "${1}" 1>&2
  echo "Failing command at ${BASH_SOURCE[1]}:${BASH_LINENO[0]}" 1>&2
  echo 'Stack trace:' 1>&2
  local n=1
  while caller $n; do
    ((n++))
  done 1>&2
  exit 1
}

# Activate error handling
# trap 'error_handler "An error occurred."' ERR

if [[ "${SOURCE}" == "youtube" ]]; then
    WORKSPACE="GE_YT"
    if [[ -z "${SECRETS_SAS_TOKEN}" ]]; then
        echo 'Please provide SECRETS_SAS_TOKEN for secrets storage' 1>&2
        exit 1
    fi

    if [[ -z "${SECRETS_FILE}" ]]; then
        echo 'Please provide path to SECRETS_FILE' 1>&2
        exit 1
    fi
    
    echo ${WORKSPACE}

    # Download secrets file from Azure Blob Storage
    secrets_download=$(az storage blob download --no-progress --container-name you-tube \
        --name "${SECRETS_FILE}" --file "${WORKSPACE}"/secrets/youtube.json --account-name \
        dpconfig --sas-token "${SECRETS_SAS_TOKEN}" | jq -r '.')

    printf "done downloading secrets file to ${WORKSPACE}/secrets/youtube.json\n"

    ls -l "${WORKSPACE}"/secrets
    echo ''
    SECRETS_FILE="${WORKSPACE}/secrets/youtube.json"

    # Execute the data pipeline script
    python -u "${WORKSPACE}/${PYSCRIPT:-datapipeline.py}" \
        --secrets_file="${SECRETS_FILE}" \
        --config_file="${CONFIG_FILE}" \
        --storage_account="${STORAGE_ACCOUNT}" \
        --container="${CONTAINER_NAME}" \
        --folder_path="${FOLDER_PATH}"

    echo "${SOURCE} script completed"
    # echo "this is a test"
fi

if [[ "${SOURCE}" == "meta_engagement" ]]; then
    WORKSPACE="GE_meta_engagement"
    if [[ -z "${SECRETS_SAS_TOKEN}" ]]; then
        echo 'Please provide SECRETS_SAS_TOKEN for secrets storage' 1>&2
        exit 1
    fi

    if [[ -z "${SECRETS_FILE}" ]]; then
        echo 'Please provide path to SECRETS_FILE' 1>&2
        exit 1
    fi

    mkdir -p "${WORKSPACE}"/secrets

    # Download secrets file from Azure Blob Storage
    secrets_download=$(az storage blob download --no-progress --container-name meta \
        --name "${SECRETS_FILE}" --file "${WORKSPACE}"/secrets/meta_engagement_secrets.json --account-name \
        dpconfig --sas-token "${SECRETS_SAS_TOKEN}" | jq -r '.')

    printf "done downloading secrets file to ${WORKSPACE}/secrets/meta_engagement_secrets.json\n"

    ls -l "${WORKSPACE}"/secrets
    echo ''
    SECRETS_FILE="${WORKSPACE}/secrets/meta_engagement_secrets.json"

    # Execute the data pipeline script
    python -u "${WORKSPACE}/${PYSCRIPT:-datapipeline.py}" \
        --secrets_file="${SECRETS_FILE}" \
        --config_file="${CONFIG_FILE}" \
        --storage_account="${STORAGE_ACCOUNT}" \
        --container="${CONTAINER_NAME}" \
        --folder_path="${FOLDER_PATH}" \
        --folder_name="${FOLDER_NAME}"

    echo "${SOURCE} script completed"
    # echo "this is a test"
fi
