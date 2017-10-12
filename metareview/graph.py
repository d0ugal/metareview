import datetime
from collections import defaultdict

import pendulum
from bokeh import plotting
import pandas


def generate_all(gerrit):

    plotting.output_file("line.html")
    p = plotting.figure(plot_width=800, plot_height=250, x_axis_type="datetime")

    counter = defaultdict(int)
    duration = defaultdict(list)

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
        except KeyError:
            for key, value in review.items():
                print(key, str(value)[:20])
            print(review.keys())
            return

    summed = {k: sum(v) / len(v) for k, v in duration.items()}

    data = sorted(counter.items())
    df = pandas.DataFrame(data, columns=['Date', 'Review Count'])
    print(df)

    p.line(df['Date'], df['Review Count'], color='navy')
    plotting.show(p)
