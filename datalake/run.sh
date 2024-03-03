#!/usr/bin/env bash

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
    if [[ -z "${SECRETS_SAS_TOKEN}" ]]; then
        echo 'Please provide SECRETS_SAS_TOKEN for secrets storage' 1>&2
        exit 1
    fi

    if [[ -z "${SECRETS_FILE}" ]]; then
        echo 'Please provide path to SECRETS_FILE' 1>&2
        exit 1
    fi
    
    mkdir -p ./GE_YT/secrets

    secrets_download=$(az storage blob download --no-progress --container-name you-tube \
        --name "${SECRETS_FILE}" --file GE_YT/secrets/youtube.json --account-name \
        dpconfig --sas-token "${SECRETS_SAS_TOKEN}" | jq -r '.')

    printf "done downloading secrets file to GE_YT/secrets/youtube.json\n"

    ls -l GE_YT/secrets
    echo ''
    SECRETS_FILE="GE_YT/secrets/youtube.json"

    python -u "GE_YT/${PYSCRIPT:-datapipeline.py}" \
        --secrets_file="${SECRETS_FILE}" \
        --config_file="${CONFIG_FILE}" \
        --storage_account="${STORAGE_ACCOUNT}" \
        --container="${CONTAINER_NAME}" \
        --folder_path="${FOLDER_PATH}"

    echo "${SOURCE} script completed"
fi
