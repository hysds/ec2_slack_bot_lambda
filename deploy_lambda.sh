# creating virtual environment and installing dependencies
virtualenv venv -p python3
pip install -r requirements.txt

# zipping the packages and files needed for lambda
cd venv/lib/python3.6/site-packages/
zip -r9 ${OLDPWD}/lambda_function.zip .
zip -g lambda_function.zip lambda_function.py
zip -g lambda_function.zip utils.py

