def _make_filter(keys, dict):
    for key in keys:
        dict[key] = False

# Merchant filters
_msKeys = [
    '_id', 'company_name', 'corporate_address', 'cphone', 'saving',
    'cemail', 'merchant_id'
]
_mKeys = ['pics', 'special_event', 'type', 'subcat']


merchant_filter_small = {}                      # TO be used with merchant page
_make_filter(_msKeys, merchant_filter_small)

merchant_filter = merchant_filter_small.copy()  # To be used with deals catalogue
_make_filter(_mKeys, merchant_filter)

# Deal filters
_dKeys = [
    '_id', 'saving'
]
deal_filter = {}
_make_filter(_dKeys, deal_filter)
