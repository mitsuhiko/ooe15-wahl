import os
import csv
import json
from lxml import etree


def parse_color(color):
    h = color.lstrip('#')
    if len(h) == 3:
        h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2]
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return r / 255.0, g / 255.0, b / 255.0


def color_to_hex(color):
    return '#%02x%02x%02x' % (
        int(color[0] * 255),
        int(color[1] * 255),
        int(color[2] * 255),
    )


def lerp(a, b, t):
    return a + (b - a) * t


def colorize(percent, min='#e17f13', max='#c21d00'):
    min = parse_color(min)
    max = parse_color(max)
    return color_to_hex([lerp(min[x], max[x], percent)
                         for x in xrange(3)])


def build_map(result_map):
    namespaces = {
        'svg': 'http://www.w3.org/2000/svg'
    }

    def run(key, scale=1.0):
        tree = etree.parse('reference.xml')
        for path in tree.findall('.//svg:path', namespaces=namespaces):
            id = path.attrib.get('id')
            if id and len(id) == 5 and id.isdigit():
                entry = result_map.get(int(id))
                if not entry:
                    color = '#888888'
                    name = 'Unbekannt'
                else:
                    color = colorize(entry[key] / 100.0 * scale)
                    name = entry['name']
                path.attrib['fill'] = color
                path.find('svg:desc', namespaces=namespaces).text = name
        return tree

    with open('map_foreigners.svg', 'w') as f:
        f.write(etree.tostring(run('foreigners', 2.0), pretty_print=True))
    with open('map_fpoe2015.svg', 'w') as f:
        f.write(etree.tostring(run('fpoe_2015', 1.3), pretty_print=True))
    with open('map_fpoe2009.svg', 'w') as f:
        f.write(etree.tostring(run('fpoe_2009', 1.3), pretty_print=True))


def find_vote_change(results):
    for row in results['rows']:
        if row['party']['shortcut'] == u'FP\xd6':
            return row[u'previousPercent'], row[u'percent'], row['votes']
    return 0.0, 0.0, 0


by_region = {}
rv = []
rv_map = {}


if 0:
    with open('population.csv') as f:
        reader = csv.reader(f)
        titles = next(reader)[1:]
        for row in reader:
            data = dict(zip(titles, row[1:]))
            by_region[int(data['NUM'].ljust(5, '0'))] = {
                'name': data['TITLE'].decode('utf-8'),
                'foreigners': float(data['FRGNPCT']),
            }

if 1:
    with open('population_new.csv') as f:
        reader = csv.reader(f)
        titles = next(reader)
        for row in reader:
            data = dict(zip(titles, row))
            by_region[int(data['GKZ'].ljust(5, '0'))] = {
                'name': data['NAME'].decode('utf-8'),
                'foreigners': float(data['NONAUTBPCT']),
            }


for filename in os.listdir('.'):
    if not filename.endswith('.json'):
        continue

    with open(filename) as f:
        results = json.load(f)

        main_region_code = results['main']['gkz']

        for sub in results['subs']:
            region_code = sub['gkz']
            alias_code = None
            if region_code not in by_region:
                if len(results['subs']) != 1:
                    continue
                alias_code = region_code
                region_code = main_region_code
            region_stats = by_region[region_code]

            region_name = sub['region']['name']
            stats_region_name = region_stats['name']
            if region_name != stats_region_name:
                region_name = '%s [%s]' % (region_name, stats_region_name)

            last, this, votes = find_vote_change(next(
                x for x in sub['results'] if x['election'] == 'ltw'))

            item = {
                'gkz': region_code,
                'name': region_name,
                'fpoe_2009': last,
                'fpoe_2015': this,
                'fpoe_2015_votes': votes,
                'foreigners': region_stats['foreigners'],
            }

            rv.append(item)
            rv_map[region_code] = item
            if alias_code is not None:
                rv_map[alias_code] = item


rv.sort(key=lambda x: -x['fpoe_2015'])


with open('output.csv', 'w') as f:
    f.write('GKZ,Name,FPOe 2009,FPOe 2015,FPOe 2015 Votes,Foreigners\n')
    for x in rv:
        f.write(','.join(map(unicode, [
            x['gkz'],
            x['name'],
            x['fpoe_2009'],
            x['fpoe_2015'],
            x['fpoe_2015_votes'],
            x['foreigners'],
        ])).encode('utf-8') + '\n')


build_map(rv_map)
