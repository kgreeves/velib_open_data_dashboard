def generate_q_url(base_url: str, search_dict: dict) -> str:

    q_url = base_url

    for key, value in search_dict.items():
        if type(value) == list:
            for item in value:
                q_url += str(key)+'='+str(item)
        else:
            q_url += str(key) + '=' + str(value)

        q_url += '&'

    return q_url[:-1]
