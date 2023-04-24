# python3 -m venv env-pymongo-fastapi-crud
source new_venv/bin/activate
python3 -m pip install 'fastapi[all]' 'pymongo[srv]' python-dotenv
python3 -m pip install "pymongo[snappy,gssapi,srv,tls]"
python3 -m pip install uvicorn dotenv