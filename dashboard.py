from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import Select
from bokeh.plotting import figure, ColumnDataSource
import csv

data_file = "monthly_avg.csv"

monthly_data = {}
zipcodes = set()

with open(data_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        zipcode = row["zipcode"]
        month = int(row["month"])
        avg_hours = float(row["avg_response_hours"])
        if zipcode not in monthly_data:
            monthly_data[zipcode] = {}
        monthly_data[zipcode][month] = avg_hours
        if zipcode != "ALL":
            zipcodes.add(zipcode)

zipcodes = sorted(zipcodes)

zipcode1 = zipcodes[0]
zipcode2 = zipcodes[1] if len(zipcodes) > 1 else zipcodes[0]

months = list(range(1, 13))
def get_plot_data(z1, z2):
    return {
        "month": months,
        "ALL": [monthly_data["ALL"].get(m, 0) for m in months],
        "Z1": [monthly_data[z1].get(m, 0) for m in months],
        "Z2": [monthly_data[z2].get(m, 0) for m in months]
    }

source = ColumnDataSource(data=get_plot_data(zipcode1, zipcode2))

p = figure(title="Monthly Avg Response Time (hours) - 2024",
           x_axis_label="Month", y_axis_label="Avg Response Time (hours)",
           x_range=(1, 12), plot_width=800, plot_height=400)

line_all = p.line('month', 'ALL', source=source, line_width=2, color="black", legend_label="All Zipcodes")
line_z1 = p.line('month', 'Z1', source=source, line_width=2, color="blue", legend_label=f"Zipcode {zipcode1}")
line_z2 = p.line('month', 'Z2', source=source, line_width=2, color="red", legend_label=f"Zipcode {zipcode2}")

p.legend.location = "top_left"

select_zip1 = Select(title="Select Zipcode 1", value=zipcode1, options=zipcodes)
select_zip2 = Select(title="Select Zipcode 2", value=zipcode2, options=zipcodes)

def update(attr, old, new):
    z1 = select_zip1.value
    z2 = select_zip2.value
    source.data = get_plot_data(z1, z2)
    line_z1.legend_label = f"Zipcode {z1}"
    line_z2.legend_label = f"Zipcode {z2}"

select_zip1.on_change("value", update)
select_zip2.on_change("value", update)


layout = column(select_zip1, select_zip2, p)
curdoc().add_root(layout)
curdoc().title = "311 Response Time Dashboard"