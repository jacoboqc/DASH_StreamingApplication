variable = {
    'Label': 'string',
    'Datapoints': [
        {
            'Timestamp': 'datetime(2015, 1, 1)',
            'SampleCount': 123.0,
            'Average': 123.0,
            'Sum': 123.0,
            'Minimum': 123.0,
            'Maximum': 123.0,
            'Unit': 'Seconds',
            'ExtendedStatistics': {
                'string': 123.0
            }
        },
    ]
}
element = variable['Datapoints'][0]['Timestamp']
print(str(element))
