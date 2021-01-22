import json

# To be used for gathering the heating cycle data from the associated json files for each month

with open('data/NEST/2020/01/2020-01-summary.json', 'r') as json_file:
    data = json.load(json_file)
    # for day in data:
        # print(data[day]['cycles']) # this will access the cycles of each day
        # What's interesting: 'cycles -> Duration, start, end, caption, isComplete
        # print(data[day]['events'])
        # break

    for day in data:
        for cycle in data[day]['cycles']:
            caption = cycle['caption']['plainText'].split(' from')[0] # just take type of cycle
            startTime = cycle['caption']['parameters']['startTime'][:-6] # don't know if this works for all times yet
            endTime = cycle['caption']['parameters']['endTime'][:-6]
            duration = cycle['duration']
            isComplete = cycle['isComplete']
            print(caption)
            print(startTime, " to ", endTime, "seconds: ", duration)
            print("Is Complete: ", isComplete, '\n')
