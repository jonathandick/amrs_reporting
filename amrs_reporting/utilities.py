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
