## Lambda needed for the AWS instance checker bot

https://github.com/DustinKLo/ec2_monitor_bot

- Alternative to the endpoint that listens to slack API requests
    - Lambda will verify the slack signature and push the data to SQS
    - Bot will then poll SQS and process the slack interactive messages
    - Does not need to bypass AWS firewall

- Steps
    - Create virtual environment: `virtualenv venv -p python3` (use python3 environment)
    - install dependencies: `pip install -r requirements.txt`
    - Zip the package:
        - `cd venv/lib/python3.6/site-packages/`
        - `zip -r9 ${OLDPWD}/lambda_function.zip .`
        - `zip -g lambda_function.zip lambda_function.py`
        - `zip -g lambda_function.zip utils.py`
    - Upload the `lambda_function.zip` package in the AWS Lambda interface manually 
       