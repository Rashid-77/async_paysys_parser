# configuration.
# set True if you want to parse choosen direction (if it realised, of course)


to_parse = {
    'KoronaPay':{
        'Турция':True,
        'Грузия':True,
        'Таджикистан':True,
        'Узбекистан':True,
        'Киргизия':True,
        'Казахстан':True, 
        'Вьетнам':True,
        'Молдова':True,
    },
    'Unistream': {
        'Турция':True,
        'Узбекистан':True,
    },
    'Paysend':{
        'Узбекистан':True,
    },
    'Alif':{
        'Таджикистан':False,
    },
    'Unired':{
        'Таджикистан':False,
    }
}

def get_parsed_pay_names() -> list:
    ''' when somy pay system become not actual or closed, 
        then it shouldnt appear in user's subscribed list'''
    res = []
    for c in to_parse:
        for f in to_parse[c]:
            if to_parse[c][f] == True:
                res.append(c)
                break
    return res


def get_country_list(pay_system_name:str):
    countries = to_parse[pay_system_name]
    return [country for country in countries if countries[country]==True]
