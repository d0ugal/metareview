import datetime
from collections import defaultdict

import pendulum
from bokeh import plotting
from bokeh.io import export_png
import pandas


def generate_all(gerrit):

    counter = defaultdict(int)
    duration = defaultdict(list)
    project_count = defaultdict(set)

    for review in gerrit.reviews():
        try:
            date_string = review['created']
            dt = pendulum.parse(date_string)
            month = datetime.datetime(dt.year, dt.month, 1)
            counter[month] += 1
            if 'submitted' in review:
                dts = pendulum.parse(review['submitted'])
                d = (dts - dt).seconds
                duration[month].append(d)
            project_count[month].add(review['project'])
        except KeyError:
            for key, value in review.items():
                print(key, str(value)[:20])
            print(review.keys())
            return

    width = 1200
    height = 600

    summed = {k: sum(v) / len(v) for k, v in duration.items()}
    lened = {k: len(v) for k, v in project_count.items()}

    p = plotting.figure(plot_width=width, plot_height=height, x_axis_type="datetime")
    data = sorted(counter.items())
    df = pandas.DataFrame(data, columns=['Date', 'Review Count'])
    p.line(df['Date'], df['Review Count'], color='navy')
    export_png(p, filename="graphs/review_count.png")

    p = plotting.figure(plot_width=width, plot_height=height, x_axis_type="datetime")
    data = sorted(summed.items())
    df = pandas.DataFrame(data, columns=['Date', 'Average Duration'])
    p.line(df['Date'], df['Average Duration'], color='navy')
    export_png(p, filename="graphs/review_duration.png")

    p = plotting.figure(plot_width=width, plot_height=height, x_axis_type="datetime")
    data = sorted(lened.items())
    df = pandas.DataFrame(data, columns=['Date', 'Unique Projects'])
    p.line(df['Date'], df['Unique Projects'], color='navy')
    export_png(p, filename="graphs/project_count.png")
