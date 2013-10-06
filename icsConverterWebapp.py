#!/usr/bin/env python

from icalendar import Calendar, Event, LocalTimezone
from datetime import datetime, timedelta
from random import randint
from sys import exit
from os.path import expanduser,isdir
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class HeadersError(Exception):
    pass

class DateTimeError(Exception):
    pass

def check_headers(headers): 
    '''Makes sure that all the headers are exactly
    correct so that they'll be recognized as the
    necessary keys.'''
    
    valid_keys = ['End Date', 'Description',
    'All Day Event', 'Start Time', 'Private',
    'End Time', 'Location', 'Start Date', 'Subject']

    if (set(headers) != set(valid_keys)
    or len(headers) != len(valid_keys)):
        logger.error('Problem in the check_headers function. Headers: {}'.format(headers))
        raise HeadersError('Something isn\'t right with the headers.')
    else:
        return True

def clean_spaces(csv_dict):
    '''Cleans trailing spaces from the dictionary
    values, which can break my datetime patterns.'''
    clean_row = {}
    for row in csv_dict:
        for k, v in row.items():
            if v:
                clean_row.update({ k: v.strip() })
            else:
                clean_row.update({ k: None })
                
        yield clean_row

def check_dates_and_times(
        start_date = None, start_time = None,
        end_date = None, end_time = None, all_day = None
    ):
    '''Checks the dates and times to make sure everything is kosher.'''
    
    logger.debug('Date checker started.')
    
    # Gots to have a start date, no matter what.
    if start_date in ['', None]:
        logger.error('Missing a start date')
        raise DateTimeError('Missing a start date')
        return False
        
    for date in [start_date, end_date]:
        if date not in ['', None]:
            try:
                datetime.strptime(date, '%m/%d/%Y')
            except:
                logger.error('Problem with date formatting. Date: {}'.format(date))
                raise DateTimeError('Something isn\'t right with the dates.')
                return False

    for time in [start_time, end_time]:
        if time not in ['', None]:
            try: 
                time = time.replace(' ', '')
                if time[-2:].lower() in ['am','pm']:
                    datetime.strptime(time, '%I:%M%p')
                else:
                    datetime.strptime(time, '%H:%M' )
            except:
                logger.error('Problem with time formatting. Time: {}'.format(time))
                raise DateTimeError('Something isn\'t right with the times.')
                return False
    
    if all_day == None or all_day.lower() != 'true':
       if not (start_time and end_time):
           logger.error('Missing a required time field in a non-all_day event on date: {}.'.format(start_date))
           raise DateTimeError('Missing a required time field in a non-all_day event.')
           return False

    logger.debug('Date checker ended.')
    return True
   
def convert(reader_builder):

    # Filter out events with empty subjects, a required element
    # for a calendar event.
    # Code found here: http://bit.ly/Z4Pg4h

    try:
        reader_builder[:] = [d for d in reader_builder if d.get('Subject') != '']

        headers = reader_builder[0].keys()
        check_headers(headers)
    except Exception:
        logger.exception('May have been a headers problem. Raw headers were: {}'.format(reader_builder[0].keys()))
        return 'error1'        


    rownum = 0
    try:
        reader = clean_spaces(reader_builder)

        # Start calendar file
        cal = Calendar()
        cal.add('prodid', 'n8henrie.com')
        cal.add('version', '2.0')

        # Write the clean list of dictionaries to events.
        
        for row in reader:
            logger.debug('Event {} started, contents:\n{}'.format(rownum, row))
            event = Event()
            event.add('summary', row['Subject'])
            logger.info('Event {} initialiazed, subject: {}'.format(rownum, row['Subject']))

            # If marked as an "all day event," ignore times.
            # If start and end date are the same
            # or if end date is blank, default to a single 24-hour event.

            try:
                check_dates_and_times(
                    start_date = row.get('Start Date'),
                    start_time = row.get('Start Time'),
                    end_date = row.get('End Date'),
                    end_time = row.get('End Time'),
                    all_day = row.get('All Day Event')
                )
            except:
                return 'error4'

            if row.get('All Day Event') != None and row['All Day Event'].lower() == 'true':
                
                # All-day events will not be marked as 'busy'
                event.add('transp', 'TRANSPARENT')
                
                event.add('dtstart', datetime.strptime(row['Start Date'], '%m/%d/%Y' ).date())
                if row.get('End Date') in ['', None]:
                    event.add('dtend', (datetime.strptime(row['Start Date'], '%m/%d/%Y' ) + timedelta(days=1)).date())
                else:
                    event.add('dtend', (datetime.strptime(row['End Date'], '%m/%d/%Y' ) + timedelta(days=1)).date())

            # Continue processing events not marked as "all day" events.
            else:

            # Events with times should be 'busy' by default
                event.add('transp', 'OPAQUE')

                # Get rid of spaces
                row['Start Time'] = row['Start Time'].replace(' ', '')
                row['End Time'] = row['End Time'].replace(' ', '')
                
                # Allow either 24 hour time or 12 hour + am/pm   
                if row['Start Time'][-2:].lower() in ['am','pm']:
                    event.add('dtstart', datetime.strptime(row['Start Date'] + row['Start Time'], '%m/%d/%Y%I:%M%p' ))
                else:
                    event.add('dtstart', datetime.strptime(row['Start Date'] + row['Start Time'], '%m/%d/%Y%H:%M' ))
                    
                # Allow blank end dates (assume same day)
                if row.get('End Date') in ['', None]:
                    row['End Date'] = row['Start Date']                
                
                if row['End Time'][-2:].lower() in ['am','pm']:
                    event.add('dtend', datetime.strptime(row['End Date'] + row['End Time'], '%m/%d/%Y%I:%M%p' ))
                else:
                    event.add('dtend', datetime.strptime(row['End Date'] + row['End Time'], '%m/%d/%Y%H:%M' ))

            if row['Description']:
                event.add('description', row['Description'])
            if row['Location']:
                event.add('location', row['Location'])

            event.add('dtstamp', datetime.replace( datetime.now(), tzinfo=LocalTimezone() ))
            event['uid'] = str(randint(1,10**30)) + datetime.now().strftime('%Y%m%dT%H%M%S') + '___n8henrie.com'

            cal.add_component(event)
            rownum += 1
    except Exception:
        # Headers probably okay but problem in body
        logger.exception('Problem in body. Made it through {} rows.'.format(rownum))
        return 'error2'            

    try:
        finalFile = cal.to_ical()
    except Exception:
        # Error finalizing file.
        logger.exception('Final file attempted to write:\n\n{}'.format(cal))
        return 'error3'

    return finalFile
