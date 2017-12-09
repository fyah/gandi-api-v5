import requests, re

def get_current_public_ip(ip_services, debug=False):
    '''
    resolve public ip using simple service
    '''
    for service in ip_services:
        try:
            r = requests.get(service)
            res = r.content.split('\n')[0]
            if re.match('\d+\.\d+\.\d+\.\d+', res):
                return res
        except Exception as e:
            #there was a problem resolving our public with the service...
            if debug:
                print 'Failed to resolve public ip using %s' % service
                print e
            #try with next
            continue


####run
if __name__ == "__main__":
    import yaml
    import lib_gandi_api_v5

    #load configuration
    config = yaml.safe_load(open("config.yml"))

    #get our public ip
    current_ip = get_current_public_ip(ip_services=config['ip_services'], debug=config['debug'])
    if current_ip:
        #connect to the api, for the given key
        g = lib_gandi_api_v5.gandi_api_v5(api_url=config['api_url'], api_key=config['api_key'], debug=config['debug'])
        #get zones
        g.get_zones()
        #get records
        g.get_records()
        for zone_name in config['records_to_update']:
            for record_to_check in config['records_to_update'][zone_name]:
                configured_ip_record = g.get_record(zone_name, record_to_check)
                if configured_ip_record:
                    configured_ip = configured_ip_record['rrset_values'][0]
                    if config['debug']:
                        print 'We have %s in DNS, and %s found' % (configured_ip, current_ip)
                    if configured_ip != current_ip:

                        g.update_record(configured_ip_record['rrset_href'], {'rrset_values': [current_ip]})

                        if config['debug']:
                            print 'Need to update'
                            check_ok = False
                            #verify
                            g.get_records()
                            configured_ip_record = g.get_record(zone_name, record_to_check)
                            if configured_ip_record:
                                configured_ip = configured_ip_record['rrset_values'][0]
                                if configured_ip == current_ip:
                                    check_ok = True

                            if check_ok:
                                print 'Verified update OK'
                            else:
                                print 'Update not verified'
    elif config['debug']:
        print 'Failed to get current public IP'
