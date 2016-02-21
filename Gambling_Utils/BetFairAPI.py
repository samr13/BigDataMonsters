import urllib2
import json
from Eternal_Utils.CommonUtils import CommonUtils

import datetime

from Proxy import ProxyHandler


class OddsGeneration:
    def __init__(self):
        self.api_base_url = 'https://api.betfair.com/exchange/betting/json-rpc/v1'
        self.APP_KEY_DELAYED = CommonUtils.get_environ_variable('BET_FAIR_APP_KEY_DELAYED')
        self.APP_KEY = CommonUtils.get_environ_variable('BET_FAIR_APP_KEY_NONDELAYED')
        self.BET_FAIR_SESSION_TOKEN = ''
        self.BET_FAIR_USERNAME = CommonUtils.get_environ_variable('BET_FAIR_USERNAME')
        self.BET_FAIR_PASSWORD = CommonUtils.get_environ_variable('BET_FAIR_PASSWORD')
        self.api_call_headers = {}

    # TODO - We have to use a proxy to get this to work
    def get_session_key_and_set_headers(self):
        """
        Gets session key from betfair, these last 20 minutes and have to get regenerated.
        Additionally we have to create some sort of proxy for them since they hate Freedom.
        :return: session key
        """
        session_key_headers = {
            'Accept': 'application/json',
            'X-Application': self.APP_KEY_DELAYED
        }
        data = 'username=' + self.BET_FAIR_USERNAME + '&password=' + self.BET_FAIR_PASSWORD
        session_key_url = "https://identitysso.betfair.com/api/login"

        try:
            session_key_request = urllib2.Request(session_key_url, data, session_key_headers)
            proxy = ProxyHandler()
            opener = proxy.url_request()
            session_key_response = opener.open(session_key_request)
            response = session_key_response.read()
            json_response = json.loads(response)
            if json_response['status'] == 'SUCCESS':
                print json_response['token']
                self.BET_FAIR_SESSION_TOKEN = json_response['token']
                self.api_call_headers = {'X-Application': self.APP_KEY_DELAYED,
                                         'X-Authentication': self.BET_FAIR_SESSION_TOKEN,
                                         'content-type': 'application/json'}
            else:
                return False

        except urllib2.HTTPError:
            print 'Oops no service available at ' + str(session_key_url)
        except urllib2.URLError:
            print 'No service found at ' + str(session_key_url)

    def call_api(self, json_request):
        """
        This is our API caller, other functions pass in requests and it gets the info.
        :param json_request: request for information we want, based on method
        :return: returns json response from API
        """
        try:
            self.get_session_key_and_set_headers()
            request = urllib2.Request(self.api_base_url, json_request, self.api_call_headers)
            response = urllib2.urlopen(request)
            json_response = response.read()
            return json_response

        except urllib2.HTTPError:
            print 'Invalid Operation from the service: ' + str(self.api_base_url)
        except urllib2.URLError:
            print 'No service found at ' + str(self.api_base_url)

    def get_list_events_filtered(self, game):
        self.get_session_key_and_set_headers()
        json_request = '[{ "jsonrpc": "2.0", "method": "SportsAPING/v1.0/listEventTypes", ' \
                       '"params": { "filter": { "textQuery":"' + game + '" } },"id": 1}]'
        response = self.call_api(json_request)
        return response

    def get_particular_event_list(self, game_id):
        """
        Gets information for event types that bet-fair handles
        :return: returns json of events
        """
        event_type_req = '[{"jsonrpc": "2.0","method": "SportsAPING/v1.0/listEvents","params": ' \
                         '{"filter": {"eventTypeIds": ["' + game_id + '"], "marketStartTime": {"from": ' \
                         '"2016-02-01T00:00:00Z","to": "2016-02-28T23:59:00Z"}}},"id": 1}]'
        response = self.call_api(event_type_req)
        event_list_json = json.loads(response)

        try:
            event_list = event_list_json[0]['result']
            return event_list
        except KeyError:
            print 'Error while trying to get event types: ' + str(event_list_json['error'])
