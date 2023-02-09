import finviz as fv
import pandas as pd
import yfinance as yf
import datetime as dt


def parse_fv_insiders(df):
    df.Date = df.Date.apply(dt.datetime.strptime, args=('%b %d',))
    df['SEC Form 4'] = df['SEC Form 4'].apply(dt.datetime.strptime, args=('%b %d %I:%M %p',))
    today = dt.date.today()
    today_md = pd.to_datetime(today.replace(year = 1900))
    today_md_sec = today_md + dt.timedelta(days=1)
    df.Date = df.Date.apply(lambda x: x.replace(year = today.year-1) if x >= today_md else x.replace(year = today.year))
    df['SEC Form 4'] = df['SEC Form 4'].apply(lambda x: x.replace(year = today.year-1) if x > today_md_sec else x.replace(year = today.year))

    df.columns = ['ticker', 'insider', 'position', 'date', 'transaction', 'price', 'shares', 'value', 'total_shares', 'SEC']

    thousands = ['shares', 'value', 'total_shares']
    for thou in thousands:
        df[thou] = df[thou].str.replace(',', '')

    strings = ['insider', 'position', 'transaction']
    for obj in strings:
        df[obj] = df[obj].str.lower()
        
    df = df.astype({'ticker': 'object', 'insider': 'object', 'position': 'object', 'date': 'datetime64[ns]', 'transaction': 'object', 'price': 'float', 'shares': 'int64', 'value': 'int64', 'total_shares': 'int64', 'SEC': 'datetime64[ns]'})
    df.date = df.date.dt.date
    #df.drop(['total_shares', 'SEC'], axis = 1, inplace = True)
    return df


def fv_insiders(ticker):
    df = pd.DataFrame(fv.get_insider(ticker))
    df.insert(0,'ticker', ticker)
    #return df
    return parse_fv_insiders(df)


def fv_last_insiders(side = None):
    
    from finviz.helper_functions.request_functions import http_request_get
    from lxml import etree

    if side == 'buy':
        url = "https://finviz.com/insidertrading.ashx?tc=1"
    elif side == 'sell':
        url = "https://finviz.com/insidertrading.ashx?tc=2"
    else:
        url = "https://finviz.com/insidertrading.ashx"

    page = http_request_get(url, parse=False)
    
    start = '<table class="body-table w-full bg-[#d3d3d3]">'
    end = '<span class="body-table">'

    data = start + page[0].split(end)[0].split(start)[1]
    out = []
    table = etree.HTML(data).find("body/table")
    rows = iter(table)
    headers = [col.text for col in next(rows)]
    for row in rows:
        values = [col.text for col in row]
        values[0] = [col.text for col in row[0]][0]
        values[1] = [col.text for col in row[1]][0]
        values[9] = [col.text for col in row[9]][0]
        out.append(dict(zip(headers, values)))
        
    df = pd.DataFrame.from_dict(out)

    return parse_fv_insiders(df)


def yf_insiders(ticker):
    df = yf.Ticker(ticker).insiders
    df.Date = df.Date.apply(dt.datetime.strptime, args=('%b %d, %Y',))
    interpuction = ['.', '-', ' ']

    for n, info in enumerate(df.Insider):
        name = str()
        to_replace = str()
        interpuction = ['.', '-', "'", ',']
        for sign in info:
            if sign in interpuction:
                to_replace += sign
            elif sign.isupper() or sign == ' ':
                name += sign
                to_replace += sign
            else:
                break
        name = name[:-1].lower()
        position = info.lower().replace(to_replace[:-1].lower(), '')
        df.loc[n, 'insider'] = name
        df.loc[n, 'position'] = position
    df.drop('Insider',axis = 1, inplace = True)

    for n, info in enumerate(df.Transaction):
        #drop nan transactions
        if not isinstance(info, str):
            df.drop(n, inplace=True)
            continue

        #extract price from transaction
        price = str()
        for k in info:
            if k.isdigit() or k in ['.', '-']:
                price += k
        price = price[:-1]
        prices = [float(x) for x in price.split('-')]
        price = sum(prices)/len(prices)
        df.loc[n, 'price'] = price

        #extract transaction type from transaction
        data = info.lower()
        if 'purchase' in data:
            df.loc[n, 'Transaction'] = 'buy'
        elif 'sale' in data:
            df.loc[n, 'Transaction'] = 'sale'
        elif 'conversion' in data:
            df.loc[n, 'Transaction'] = 'conversion'
        elif 'stock' in data:
            df.loc[n, 'Transaction'] = 'award'
        else:
            df.drop(n, inplace=True)

    df.columns = [x.lower() for x in df.columns]
    df = df[['insider', 'position', 'date', 'transaction', 'price', 'shares', 'value']]

    df.reset_index(inplace=True, drop = True)
    df.insert(0, 'ticker', ticker)
    
    return df