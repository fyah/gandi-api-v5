import requests, json

class gandi_api_v5(object):

    def __init__(self, api_url, api_key, debug=False):
        self.api_url = api_url
        self.api_key = api_key
        self.debug = debug

        #variables
        self.zones = []
        self.records = {}

    def get_zones(self):
        '''
        curl -H "X-Api-Key: $APIKEY" https://dns.api.gandi.net/api/v5/zones
        '''
        url = self.api_url + '/zones'
        u = requests.get(url, headers={"X-Api-Key":self.api_key})
        json_object = json.loads(u._content)
        if u.status_code == 200:
            self.zones = json_object
        elif self.debug:
            print 'Error: HTTP Status Code ', u.status_code, 'when trying to get Zone UUID'
            print  json_object

    def get_records(self):
        '''
        curl -H "X-Api-Key: $APIKEY" \
            https://dns.api.gandi.net/api/v5/zones/<UUID>/records
        '''
        for zone in self.zones:
            url = zone['zone_href'] + '/records'
            u = requests.get(url, headers={"X-Api-Key":self.api_key})
            json_object = json.loads(u._content)
            if u.status_code == 200:
                self.records[zone['name']] = json_object
            elif self.debug:
                print 'Error: HTTP Status Code ', u.status_code, 'when trying to get Zone UUID'
                print  json_object

    def get_record(self, zone_name, record_rrset_name):
        if zone_name in self.records:
            for record in self.records[zone_name]:
                if record['rrset_name'] == record_rrset_name:
                    return record

    def update_record(self, record_url, record_payload):
        '''
        curl -X POST -H "Content-Type: application/json" \
             -H "X-Api-Key: $APIKEY" \
             -d '{"rrset_ttl": 10800,
                  "rrset_values": ["<VALUE>"]}' \
             https://dns.api.gandi.net/api/v5/zones/<UUID>/records/<NAME>/<TYPE>
        '''
        headers = {"Content-Type": "application/json", "X-Api-Key":self.api_key}
        u = requests.put(record_url, data=json.dumps(record_payload), headers=headers)
        json_object = json.loads(u._content)

        if u.status_code == 201:
            if self.debug:
                print 'Status Code:', u.status_code, ',', json_object, ', IP updated for', record_url
            return True
        elif self.debug:
            print 'Error: HTTP Status Code ', u.status_code, 'when trying to update IP from subdomain', record_url
            print  json_object
