#!/usr/bin/python3

import sys
import csv
import argparse
from peloton import PelotonWorkout

parser = argparse.ArgumentParser()
parser.add_argument("output", nargs=1)
args = parser.parse_args()

def mkdict(ent):
  res = {
    'created': "%04d-%02d-%02d" % (
        ent.created.year, ent.created.month, ent.created.day),
    'type': ent.fitness_discipline,
    'instructor': ent.ride.instructor.name,
    'title': ent.ride.title,
  }

  if ent.fitness_discipline == 'cycling':
    res['distance'] = ent.metrics.distance_summary.value
    res['output'] = ent.metrics.output_summary.value
    res['calories'] = ent.metrics.calories_summary.value
    res['cycling_duration'] = ent.ride.duration
  elif ent.fitness_discipline == 'stretching':
    res['stretching_duration'] = ent.ride.duration
  elif ent.fitness_discipline == 'strength':
    res['strength_duration'] = ent.ride.duration
  elif ent.fitness_discipline == 'yoga':
    res['yoga_duration'] = ent.ride.duration
  elif ent.fitness_discipline == 'meditation':
    res['meditation_duration'] = ent.ride.duration
  else:
    print("Unknown type: %s" % ent.fitness_discipline)

  return res

def main():
  fs = ['created', 'type', 'instructor', 'title',
        'cycling_duration', 'stretching_duration', 'strength_duration',
        'meditation_duration', 'yoga_duration', 'distance', 'output',
        'calories']
  with open(args.output[0], 'w') as f:
    writer = csv.DictWriter(f, fieldnames=fs, quoting=csv.QUOTE_NONNUMERIC)

    ws = PelotonWorkout.list()
    writer.writeheader()
    for w in ws:
        writer.writerow(mkdict(w))

main()
