import nose
import nose.tools
import icsConverterWebapp

def test_headers_pass():
    '''Should return true.'''
    headers_list = [
        'End Date', 'Description',
        'All Day Event', 'Start Time', 'Private',
        'End Time', 'Location', 'Start Date', 'Subject'
    ]
    
    assert icsConverterWebapp.check_headers(headers_list)

@nose.tools.raises(icsConverterWebapp.HeadersError)
def test_bad_headers_fail():
    '''Test that bad header fails.'''
    headers_list = [
        'End Date', 'Description',
        'All Day Event', 'Start Time', 'Private',
        'End Time', 'Location', 'Start Date', 'Subjects'
    ]
    
    icsConverterWebapp.check_headers(headers_list)

@nose.tools.raises(icsConverterWebapp.HeadersError)
def test_missing_headers_fail():
    '''Test that missing header fails.'''
    headers_list = [
        'Subject'
    ]
    
    icsConverterWebapp.check_headers(headers_list)

@nose.tools.raises(icsConverterWebapp.HeadersError)
def test_extra_headers_fail():
    '''Test that extra header fails.'''
    headers_list = [
        'End Date', 'Description',
        'All Day Event', 'Start Time', 'Private',
        'End Time', 'Location', 'Start Date', 'Subject', 'Subject'
    ]
    
    icsConverterWebapp.check_headers(headers_list)

def test_spaces_trimmed():
    '''Test that spaces are removed.'''
    dict_with_spaces = [{'this': ' that '}]
    
    assert list(icsConverterWebapp.clean_spaces(dict_with_spaces)) == [{'this': 'that'}]

def test_none_is_okay():
    '''Test that None fields don't raise errors.'''
    dict_with_spaces = [{'this': None}]
    
    assert list(icsConverterWebapp.clean_spaces(dict_with_spaces)) == [{'this': None}]

def test_dates_and_times_checker():
    '''Proper dates and times for non-all_day event.'''
    start_time = '07:00 pm'
    start_date = '01/01/2014'
    end_time = '22:00'
    end_date = '01/02/2014'
    all_day = 'FALSE'
    
    assert icsConverterWebapp.check_dates_and_times(
        start_date = start_date,
        start_time = start_time,
        end_date = end_date,
        end_time = end_time,
        all_day = all_day
    )

@nose.tools.raises(icsConverterWebapp.DateTimeError)
def test_two_digit_year_fails():
    '''Two-year dates gives an error.'''
    all_day = 'TRUE'
    start_date = '01/01/13'
    
    icsConverterWebapp.check_dates_and_times(start_date = start_date, all_day = all_day)

@nose.tools.raises(icsConverterWebapp.DateTimeError)
def test_two_digit_year_fails():
    '''Two-year dates gives an error.'''
    all_day = 'TRUE'
    start_date = '01/01/13'
    
    icsConverterWebapp.check_dates_and_times(start_date = start_date, all_day = all_day)


# result = nose.run()