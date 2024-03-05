

To use Selenium along with a ChromeDriver in a Serverless Framework project for AWS Lambda, you indeed need to handle Python dependencies correctly and include the ChromeDriver binary in your deployment package. The serverless-python-requirements plugin is essential for this, as it bundles your Python dependencies, including Selenium, correctly for Lambda. Additionally, you'll need to include the ChromeDriver and a headless Chrome browser binary in your deployment because AWS Lambda does not have these installed.


## Deploy
`sls deploy`


## Invoke
`sls invoke -f check-ll-submission`


## Remove
https://www.serverless.com/framework/docs/providers/aws/cli-reference/remove
`sls remove`



## Run
1. Activate the virtualenv
2. `pip install -r requirements.txt`
3. `python3 app.py`

```
--interactive (or -i): to run the script in interactive mode.
--headless (or -h): to run Chrome in headless mode.
```


## Guides

### Using Environment Variables
https://www.serverless.com/framework/docs/environment-variables
To use environment variables in your serverless.yml file, you can use the ${env:MY_ENV_VAR} syntax. This is useful for referencing environment variables in your serverless.yml file, or for using environment variables in your Lambda functions.
```
useDotenv: true
```
