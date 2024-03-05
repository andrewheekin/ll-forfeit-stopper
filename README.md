

To use Selenium along with a ChromeDriver in a Serverless Framework project for AWS Lambda, you indeed need to handle Python dependencies correctly and include the ChromeDriver binary in your deployment package. The serverless-python-requirements plugin is essential for this, as it bundles your Python dependencies, including Selenium, correctly for Lambda. Additionally, you'll need to include the ChromeDriver and a headless Chrome browser binary in your deployment because AWS Lambda does not have these installed.




## Run
1. Activate the virtualenv
2. `pip install -r requirements.txt`
3. `python3 app.py`

```
--interactive (or -i): to run the script in interactive mode.
--headless (or -h): to run Chrome in headless mode.
```


## TODO
1. deploy to AWS
2. 