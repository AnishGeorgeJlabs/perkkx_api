def _make_filter(keys, dict):
    for key in keys:
        dict[key] = False

# Merchant filters
_msKeys = [
    '_id', 'company_name', 'corporate_address', 'cphone', 'saving',
    'cemail', 'merchant_id'
]
_mKeys = ['pics', 'special_event', 'type', 'subcat',
          'cuisine', 'delivery', 'cat', 'time', 'type']


merchant_filter_small = {}                      # TO be used with merchant page
_make_filter(_msKeys, merchant_filter_small)

merchant_filter = merchant_filter_small.copy()  # To be used with deals catalogue
_make_filter(_mKeys, merchant_filter)

# Deal filters
_dKeys = [
    '_id', 'saving', 'deal_cat', "gmin", "gmax", "deal_cat"
]
_dcKeys = [
    'vendor_id', 'vendor_name'
]
deal_filter = {}
_make_filter(_dKeys, deal_filter)

deal_compact_filter = deal_filter.copy()
_make_filter(_dcKeys, deal_compact_filter)