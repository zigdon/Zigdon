#!/usr/bin/python
import csv
import os
import re
import sys

with open(sys.argv[1]) as f:
  reader = csv.reader(f)
  if os.path.basename(sys.argv[1]) == 'dates.csv':
    data = []
    for line in reader:
      date, count = line
      if reader.line_num == 1:
        continue
      m = re.search(r'(\d+)-(\d+)-(\d+)', date)
      if m:
        date = 'new Date(%s, %s, %s)' % m.group(1, 2, 3)
        data.append('[%s, %d]' % (date, int(count)))

    template = """
      <html>
        <head>
          <script type='text/javascript' src='http://www.google.com/jsapi'></script>
          <script type='text/javascript'>
            google.load('visualization', '1', {{'packages':['annotatedtimeline']}});
            google.setOnLoadCallback(drawChart);
            function drawChart() {{
              var data = new google.visualization.DataTable();
              data.addColumn('date', 'Date');
              data.addColumn('number', 'Messages');
              data.addRows([
                {data}
              ]);

              var chart = new google.visualization.AnnotatedTimeLine(document.getElementById('chart_div'));
              chart.draw(data, {{displayAnnotations: true}});
            }}
          </script>
        </head>

        <body>
          <div id='chart_div' style='width: 100%; height: 100%;'></div>
        </body>
      </html>
    """

    print template.format(data=",\n".join(data))
  else:
    data = {}
    for line in reader:
      name, incoming, outgoing = line
      if reader.line_num == 1 or re.search(r'\+', name):
        continue
      m = re.search(r'(\w+)', name)
      if m:
        name = m.group(1)
      if data.get(name):
        data[name][1] += int(incoming)
        data[name][2] += int(outgoing)
      else:
        data[name] = [name, int(incoming), int(outgoing)]

    csvdata = [str(x) for x in sorted(data.values(), lambda x,y: cmp(x[1]+x[2], y[1]+y[2]), reverse=True)]

    year = None
    m = re.search(r'(\d+)', sys.argv[1])
    if m:
      year = m.group(1)

    template = """
    <html>
      <head>
        <!--Load the AJAX API-->
        <script type="text/javascript" src="https://www.google.com/jsapi"></script>
        <script type="text/javascript">
          google.load('visualization', '1.0', {{'packages':['corechart']}});
          google.setOnLoadCallback(drawChart);
          function drawChart() {{
            var data = google.visualization.arrayToDataTable([
                ['Name', 'Incoming', 'Outgoing'],
    {data}
            ]);

            var options = {{'title':'SMS for {year}',
                           'height': 2000,
                           'chartArea': {{width: '70%', height: '90%'}},
                           'isStacked': true,
                           'top': 20}};

            var chart = new google.visualization.BarChart(document.getElementById('chart_div'));
            chart.draw(data, options);
          }}
        </script>
      </head>

      <body>
        <!--Div that will hold the pie chart-->
        <div id="chart_div"></div>
      </body>
    </html>
    """

    print template.format(year=year, data=",\n".join(csvdata))

