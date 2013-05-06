from icalendar import Calendar, Event, LocalTimezone
from datetime import datetime, timedelta
from random import randint
from sys import exit
from os.path import expanduser,isdir

def CheckHeaders(headers):
    '''Makes sure that all the headers are exactly
    correct so that they'll be recognized as the
    necessary keys.'''

    valid_keys = ['End Date', 'Description',
    'All Day Event', 'Start Time', 'Private',
    'End Time', 'Location', 'Start Date', 'Subject']

    if (set(headers) != set(valid_keys)
    or len(headers) != len(valid_keys)):
        # Figure out how to return an error

        exit(1)
    else:
        pass

def CleanSpaces(csv_dict):
    '''Cleans trailing spaces from the dictionary
    values, which can break my datetime patterns.'''
    clean_row = {}
    for row in csv_dict:
        for k, v in row.items():
            if k:
                clean_row.update({ k: v.strip()})
        yield clean_row

def convert(reader_builder):

    # Filter out events with empty subjects, a required element
    # for a calendar event.
    # Code found here: http://bit.ly/Z4Pg4h

    try:
        reader_builder[:] = [d for d in reader_builder if d.get('Subject') != '']

        headers = reader_builder[0].keys()
        CheckHeaders(headers)
    except:
        return 'error1'

    try:
        reader = CleanSpaces(reader_builder)

        # Start calendar file
        cal = Calendar()
        cal.add('prodid', 'n8henrie.com')
        cal.add('version', '2.0')

        # Write the clean list of dictionaries to events.
        rownum = 0
        for row in reader:
            event = Event()
            event.add('summary', row['Subject'])

    # If marked as an "all day event," ignore times.
    # If start and end date are the same
    # or if end date is blank default to a single 24-hour event.
            if row['All Day Event'].lower() == 'true':
                event.add('transp', 'TRANSPARENT')
                event.add('dtstart', datetime.strptime(row['Start Date'], '%m/%d/%Y' ).date())
        #            pdb.set_trace()
                if row['End Date'] == '':
                    event.add('dtend', (datetime.strptime(row['Start Date'], '%m/%d/%Y' ) + timedelta(days=1)).date())
                else:
                    event.add('dtend', (datetime.strptime(row['End Date'], '%m/%d/%Y' ) + timedelta(days=1)).date())

            # Continue processing events not marked as "all day" events.
            else:

        # Allow either 24 hour time or 12 hour + am/pm
                if row['Start Time'][-2:].lower() in ['am','pm']:
                    event.add('dtstart', datetime.strptime(row['Start Date'] + row['Start Time'], '%m/%d/%Y%I:%M %p' ))
                else:
                    event.add('dtstart', datetime.strptime(row['Start Date'] + row['Start Time'], '%m/%d/%Y%H:%M' ))

        # Allow blank end dates (assume same day)
                if row['End Date'] == '':
                    row['End Date'] = row['Start Date']

                if row['End Time'][-2:].lower() in ['am','pm']:
                    event.add('dtend', datetime.strptime(row['End Date'] + row['End Time'], '%m/%d/%Y%I:%M %p' ))
                else:
                    event.add('dtend', datetime.strptime(row['End Date'] + row['End Time'], '%m/%d/%Y%H:%M' ))

            event.add('description', row['Description'])
            event.add('location', row['Location'])
            event.add('dtstamp', datetime.replace( datetime.now(), tzinfo=LocalTimezone() ))
            event['uid'] = str(randint(1,10**30)) + datetime.now().strftime('%Y%m%dT%H%M%S') + '___n8henrie.com'

            cal.add_component(event)
            rownum += 1
    except:
            return 'error2'

    try:
        finalFile = cal.to_ical()
    except:
        return 'error3'

    return finalFile
