from flask import Flask, redirect, session, request, Blueprint,flash, current_app as app
from flask_login import current_user, login_required
import os
import requests
from requests_oauthlib import OAuth2Session



oauth_blueprint = Blueprint('oauth', __name__)


### DISCORD CODE


def token_updater(token):
    session['oauth2_token'] = token

def make_session(token=None, state=None, scope=None):
    if 'http://' in app.config['OAUTH2_REDIRECT_URI']:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

    return OAuth2Session(
        client_id=app.config['OAUTH2_CLIENT_ID'],
        token=token,
        state=state,
        scope=scope,
        redirect_uri=app.config['OAUTH2_REDIRECT_URI'],
        auto_refresh_kwargs={
            'client_id': app.config['OAUTH2_CLIENT_ID'],
            'client_secret': app.config['OAUTH2_CLIENT_SECRET'],
        },
        auto_refresh_url=app.config['TOKEN_URL'],
        token_updater=token_updater)

@login_required
@oauth_blueprint.route('/discord')
def discord():
    scope = request.args.get(
        'scope',
        'identify guilds.join')
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(app.config['AUTHORIZATION_BASE_URL'])
    session['oauth2_state'] = state
    return redirect(authorization_url)

@login_required
@oauth_blueprint.route('/callback')
def callback():
    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('oauth2_state'))

    token = discord.fetch_token(
        app.config['TOKEN_URL'],
        client_secret=app.config['OAUTH2_CLIENT_SECRET'],
        authorization_response=request.url)

    session['oauth2_token'] = token
    discord = make_session(token=token)

    duser = discord.get(app.config['API_BASE_URL'] + '/users/@me').json()

    payload = {'access_token': token['access_token'], 'roles': [app.config['FREESIDE_ROLE']]}
    headers = {'Content-Type': 'application/json', 'Authorization':
               'Bot ' + app.config['BOT_TOKEN']}

    invite = requests.put(app.config['API_BASE_URL'] + '/guilds/{}/members/{}'
                          .format(app.config['GUILD_ID'], duser['id']),
                          json=payload, headers=headers)
                          
    if invite.status_code == 201:
        flash('Verified Discord')
    elif invite.status_code == 204:
        role = requests.put(app.config['API_BASE_URL'] + '/guilds/{}/members/{}/roles/{}'
                            .format(app.config['GUILD_ID'], duser['id'], app.config['FREESIDE_ROLE']),
                            headers=headers)
        if role.status_code == 204:
            flash('Verified Discord')
    else:
        flash('Something went wrong!')
    return redirect('/')

### END OF DISCORD CODE