from jwt import encode, decode

SECRET = "1234567890"
ALGORITHM = "HS256"
# varables de entorno en python, se utiliza el ,odulo dotenv
def create_token(data, secret= SECRET):
    return encode(data, secret, ALGORITHM)


def validate_token(token):
    return decode(token, secret,[ALGORITHM]) 