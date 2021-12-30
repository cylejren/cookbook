import requests


# payload = {'inUserName': 'username', 'inUserPass': 'password'}

#######################################################################
payload = {'text':'reenia@o2.pl', 'password': 'pdriver'}

with requests.Session() as s:
    p = s.post('https://www.pepperplate.com/login.aspx', data = payload)
    # print(p.text)
    r = s.get('http://www.pepperplate.com/recipes/view.aspx?id=9364787')
    print(r.text)
#######################################################################
# with requests.Session() as c:
#     url = "https://www.pepperplate.com/login.aspx"
#     USERNAME = "reenia@o2.pl"
#     PASSWORD = "pdriver"
#     c.get(url)
#     login_data = dict(inUserName=USERNAME,
#                       inUserPass=PASSWORD, next='/')
#     c.post(url, data=login_data, headers={"Referer": "HOMEPAGE"})
#     page = c.get("http://www.pepperplate.com/recipes/view.aspx?id=9364787")
#
#     print(page.content)
#######################################################################