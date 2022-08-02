def address(location):
    '''Returns formatted address for where services will be provided.'''

    if location == 'Mount Pleasant':
        location = ('890 Johnnie Dobbs Blvd.\nBldg. 3 Ste. A'
        '\nMount Pleasant, S.C. 29464')
    elif location == 'North Charleston':
        location = ('9263 Medical Plaza Dr.\nSte. B'
        '\nNorth Charleston, S.C. 29406')
    else:
        location = 'Telehealth'

    return location
