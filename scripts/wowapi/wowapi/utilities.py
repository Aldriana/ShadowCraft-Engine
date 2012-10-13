def http_datetime( dt=None ):

    if not dt:
        import datetime
        dt = datetime.datetime.utcnow()
    else:
        try:
            dt = dt - dt.utcoffset()
        except:
            pass  # no timezone offset, just assume already in UTC

    s = dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
    return s


def parse_http_datetime( datestring, utc_tzinfo=None, strict=False ):
   
    import re, datetime
    m = re.match(r'(?P<DOW>[a-z]+), (?P<D>\d+) (?P<MON>[a-z]+) (?P<Y>\d+) (?P<H>\d+):(?P<M>\d+):(?P<S>\d+(\.\d+)?) (?P<TZ>\w+)$',
                 datestring, re.IGNORECASE)
    if not m and not strict:
        m = re.match(r'(?P<DOW>[a-z]+) (?P<MON>[a-z]+) (?P<D>\d+) (?P<H>\d+):(?P<M>\d+):(?P<S>\d+) (?P<Y>\d+)$',
                     datestring, re.IGNORECASE)
        if not m:
            m = re.match(r'(?P<DOW>[a-z]+), (?P<D>\d+)-(?P<MON>[a-z]+)-(?P<Y>\d+) (?P<H>\d+):(?P<M>\d+):(?P<S>\d+(\.\d+)?) (?P<TZ>\w+)$',
                         datestring, re.IGNORECASE)
    if not m:
        raise ValueError('HTTP date is not correctly formatted')

    try:
        tz = m.group('TZ').upper()
    except:
        tz = 'GMT'
    if tz not in ('GMT','UTC','0000','00:00'):
        raise ValueError('HTTP date is not in GMT timezone')

    monname = m.group('MON').upper()
    mdict = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MAY':5, 'JUN':6,
             'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12}
    month = mdict.get(monname)
    if not month:
        raise ValueError('HTTP date has an unrecognizable month')
    y = int(m.group('Y'))
    if y < 100:
        century = datetime.datetime.utcnow().year / 100
        if y < 50:
            y = century * 100 + y
        else:
            y = (century - 1) * 100 + y
    d = int(m.group('D'))
    hour = int(m.group('H'))
    minute = int(m.group('M'))
    try:
        second = int(m.group('S'))
    except:
        second = float(m.group('S'))
    dt = datetime.datetime( y, month, d, hour, minute, second, tzinfo=utc_tzinfo )
    return dt