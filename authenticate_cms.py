import json
from pprint import pformat as pf

from flask import Flask, g
from flask_oidc import OpenIDConnect

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': 'SomethingNotEntirelySecret',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_SCOPES': [
        "profile"
#        "profile"
#        "patient/Patient.read",
#        "patient/ExplanationOfBenefit.read",
#        "patient/Coverage.read"
    ],
    'OIDC_CLIENT_SECRETS': 'client_secrets_cms.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_INSTROSPECTION_AUTH_METHOD': 'client_secret_basic',
    'OIDC_RESOURCE_CHECK_AUD': True,
    'OIDC_CALLBACK_ROUTE': '/cmsredirect'
})
oidc = OpenIDConnect(app)

def nl(line):
    return(line + "</br>")

def username():
    return str(oidc.user_getfield('email'))

def fullname():
    return str(oidc.user_getfield('name'))

def subject():
    return str(oidc.user_getfield('sub'))

def credentials():
    return str(oidc.credentials_store)

def token():
    return oidc.get_access_token()

def token_response():
    cred_json = oidc.credentials_store[subject()]
    cred = json.loads(cred_json)
    return cred['token_response']

def mrn():
    cred_json = oidc.credentials_store[subject()]
    cred = json.loads(cred_json)
    return cred['token_response']['patient']

def access_json_dump(fp):
    acc = {"patient": mrn(), "access_token": token()}
    return json.dump(acc, fp)

@app.route('/')
def va_home():
    if oidc.user_loggedin:
        return nl('Hello, ' + fullname() + "  (Username: %s) " % username()) \
            + nl('<a href="/authenticate">Re-authenticate</a> ') \
            + nl('<a href="/logout">Log out</a>')
    else:
        return nl('Welcome anonymous,') \
            + nl('<a href="/authenticate">Authenticate</a>') 

@app.route('/authenticate')
@oidc.require_login
def auth():
    filename = 'accesscodes/' + subject() + ".json"
    tokenfile = open(filename, "w")
    access_json_dump(tokenfile)
    tokenfile.close()

    credfile = open('credentials.json', 'w')
    credfile.write(oidc.credentials_store[subject()])
    credfile.close()

    return nl('Hello, ' + fullname()) \
        + nl('Subject: ' + subject()) \
        + nl('Token saved in ' + filename) \
        + nl('<a href="/">Return</a>') \
        + nl("") \
        + nl("Token Response:") \
        + nl("") \
        + nl(json.dumps(token_response())) \
        + nl("") \
        + nl("Patient: ") \
        + nl(str(mrn()))

@app.route('/logout')
def logout():
    oidc.logout()
    return 'Hi, you have been logged out! <a href="/">Home</a>'

if __name__ == '__main__':
    app.run()