import pprint
import os
import warnings
import requests

from oauthenticator.generic import GenericOAuthenticator

class RucioAuthenticator(GenericOAuthenticator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.enable_auth_state = True

    def exchange_token(self, token):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
            'subject_token': token,
            'scope': 'openid email profile',
            'audience': 'rucio'
        }
        response = requests.post(self.token_url, data=params)
        refresh_token = response.json()['access_token']
        return refresh_token
    
    async def pre_spawn_start(self, user, spawner):
        auth_state = await user.get_auth_state()
        pprint.pprint(auth_state)
        if not auth_state:
            # user has no auth state
            return
        
        # define some environment variables from auth_state
        spawner.environment['ACCESS_TOKEN'] = auth_state['access_token']
        spawner.environment['REFRESH_TOKEN'] = self.exchange_token(auth_state['access_token'])

c.JupyterHub.authenticator_class = RucioAuthenticator

# enable authentication state
c.GenericOAuthenticator.enable_auth_state = True

if 'JUPYTERHUB_CRYPT_KEY' not in os.environ:
    warnings.warn(
        "Need JUPYTERHUB_CRYPT_KEY env for persistent auth_state.\n"
        "    export JUPYTERHUB_CRYPT_KEY=$(openssl rand -hex 32)"
    )
    c.CryptKeeper.keys = [os.urandom(32)]
    