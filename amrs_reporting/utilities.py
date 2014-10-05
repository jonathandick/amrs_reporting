def get_var(d,var_name):
    if var_name in d and d[var_name] != '' : return d[var_name]
    else : return None

def get_var_from_request(request,var_name):
    if var_name in request.POST and request.POST[var_name] != '' : return request.POST[var_name]
    elif var_name in request.GET and request.GET[var_name] != '' : return request.GET[var_name]
    else : return None


def my_fetcher(url):
    if url.startswith('/static/amrs_reports/images/'):                        
        with open(os.path.join('home/jdick/openmrs_env/reporting/amrs_reports',url)) as asset:
            contents = asset.read()
        return dict(string=contents)
    else:
        return default_url_fetcher(url)


def get_val_from_row(row,col_name) :
    if row[col_name] is None : return ''
    else : return row[col_name]

#from https://djangosnippets.org/snippets/2228/
import re
def get_device(request):

    device = {}
    ua = request.META.get('HTTP_USER_AGENT', '').lower()
    print ua
    if ua.find("iphone") > 0:
        device['iphone'] = "iphone" + re.search("iphone os (\d)", ua).groups(0)[0]

    if ua.find("ipad") > 0:
        device['ipad'] = "ipad"

    if ua.find("android") > 0:
        device['android'] = "android" #+ re.search("android (\d\.\d)", ua).groups(0)[0]

    if ua.find("blackberry") > 0:
        device['blackberry'] = "blackberry"

    if ua.find("windows phone os 7") > 0:
        device['winphone7'] = "winphone7"

    if ua.find("iemobile") > 0:
        device['winmo'] = "winmo"

    if ua.find("huawei") >0 :
        device['huawei'] = "huawei"


    if ua.find("firefox/11.0") :
        device['firefox'] = "firefox"
 
    # either desktop, or something we don't care about.
    if not device :
        device['baseline'] = "baseline"
        device['is_mobile'] = False
    else : device['is_mobile'] = True

    # spits out device names for CSS targeting, to be applied to <html> or <body>.
    #device['classes'] = " ".join(v for (k,v) in device.items())
    return device
    #return {'device': device }
