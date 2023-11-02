This sub directory should contains anything to do with the datalake pipelines.

## Docker

Installing docker on your local machine for testing:

[Docker Desktop](https://www.docker.com/products/docker-desktop/)

- Using the above you should be able to install docker on your windows, linux or mac laptop.
- Just know this can be a bit memory expensive so make sure you are not running alot of memory intensive apps.
- Also stop the service when you are not running any docker containers.
- Also remember to run your docker with the `--rm` flag so as to remove the container when it is done (consumes memory).

### Building the docker container:
 - From the root of the repo run `cd datalake && docker build -t girleffect .`
 - Note that in the above code the `girleffect` is the resulting image name.

### Running the docker container:

```YAML
docker run --rm -it -v "$HOME/.azure-docker:/root/.azure" \
    -e PYSCRIPT="GE_YT/datapipeline.py" \
    -e SECRETS_FILE=GE_YT/secrets/yegna.json \
    -e CONFIG_FILE=GE_YT/configs/youtube.yml \
    -e STORAGE_ACCOUNT="azure cloud storage" \
    -e CONTAINER="container_name" \
    -e SLACK_BOT_TOKEN="slack bot token here" \
    -e SOURCE="youtube" \
    girleffect

```

- From the above command there are environment variables that need to be passed to the pythn script passed a `-e ENV_NAME=ENV_VALUE`
- Also note that we are passing in `"$HOME/.azure-docker:/root/.azure"` what this does is load the azure credentials into the docker container. See this link for more details [Azure Cli Local Docker]("https://endjin.com/blog/2022/09/using-azcli-authentication-within-local-containers)
- We pass in the `SLACK_BOT_TOKEN` to be used to send notifications to `data-pipelines-alerts` slack channel in case of failures
- `girleffect` is the docker image name that is to be run
- `--rm` just ensures that the container is deleted ones it is done running.
- `-it` means running the docker container in interactive mode and allowing us to see the logs as it runs. Other options is `-d` meaning silent.
- Environment value `SOURCE` will determine which pipeline is run. For youtube we need to pass in `youtube`

### TODO:
- Upload the docker image to Azure ACR
- Use the uploaded image to run the pipeline in azure
- Possibly implement download of secrets from azure cloud storage? or from azure data vault.
- Also implement the environment vairables on the azure app definition. 
