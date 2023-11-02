#!/usr/bin/env bash
if [[ "${SOURCE}" == "youtube" ]]; then
    
    mkdir -p GE_YT/secrets

    python -u GE_YT/"${PYSCRIPT:-datapipeline.py}" \
        --secrets_file="${SECRETS_FILE}" \
        --config_file="${CONFIG_FILE}" \
        --storage_account="${STORAGE_ACCOUNT}" \
        --container="${CONTAINER}"

    echo '"${SOURCE}" script completed successfully'
fi
