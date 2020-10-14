import asyncio
import json
import quart
import sys
import typing
import werkzeug.routing

import area
import calculator

try:
    import neopixel
except NotImplementedError:
    from rpi_mock import neopixel

try:
    import RPi.GPIO
except ModuleNotFoundError:
    from rpi_mock import RPi

app = quart.Quart("LED Controller", static_url_path='')
app.secret_key = "LedController_ChangeThisKeyForInstallation"


class ColorConverter(werkzeug.routing.BaseConverter):
    app = None

    def to_python(self, value: str) -> calculator.ColorRGBX:
        return list(map(int, value.split(".")))

    def to_url(self, obj: calculator.ColorRGBX) -> str:
        return ".".join(map(str, obj))


app.url_map.converters['color'] = ColorConverter

strips_data: list = []
area_data: list = []
lights_data: list = []

available_strips = dict()
available_areas: typing.Dict[str, area.Area] = dict()


def initialize_config(config_file: str = 'default.config'):
    global strips_data
    global area_data

    with open(config_file, 'r') as data:
        json_data = json.load(data)
        if 'secret_key' in json_data:
            app.secret_key = json_data['secret_key']
        else:
            raise ValueError(f'missing entry secret_key in {config_file}')
        if 'strips' in json_data:
            strips_data = json_data['strips']
        else:
            raise ValueError(f'missing entry strips in {config_file}')
        if 'areas' in json_data:
            area_data = json_data['areas']
        else:
            raise ValueError(f'missing entry areas in {config_file}')


@app.before_serving
async def _start_server():
    _init_strips()
    _init_areas()
    RPi.GPIO.setmode(RPi.GPIO.BCM)
    for light in lights_data:
        RPi.GPIO.setup(light['gpio'], RPi.GPIO.OUT, initial=0)
    for strip in strips_data:
        RPi.GPIO.setup(strip['power_gpio'], RPi.GPIO.OUT, initial=0)


@app.after_serving
async def _stop_server():
    RPi.GPIO.cleanup()


def _init_strips():
    global available_strips
    for strip_data in strips_data:
        if strip_data['id'] not in available_strips:
            strip = neopixel.NeoPixel(strip_data['count'], strip_data['gpio'], strip_data['freq'], strip_data['dma'],
                                      strip_data['invert'], strip_data['brightness'], strip_data['channel'],
                                      eval(strip_data['type']))
            strip.begin()
            available_strips[strip_data['id']] = strip_data
            available_strips[strip_data['id']]['strip'] = strip


def _init_areas():
    global available_areas
    global available_strips

    for ad in area_data:
        area_obj = area.Area(ad['name'])
        for s in ad['strips']:
            if len(s) == 2:
                area_obj.add_strip(s[0], s[1])
            if len(s) == 3:
                strip = available_strips[s[2]]
                if strip:
                    area_obj.add_strip(s[0], s[1], available_strips[s[2]])

        available_areas[ad['name']] = area_obj


def convert_to_dict(obj):
    obj_dict = dict()
    for key in dir(obj):
        if not key.startswith("_"):
            value = getattr(obj, key)
            if not callable(value):
                obj_dict[key] = value
    return obj_dict


@app.route('/')
async def get_rich_client():
    #return f'test', 200
    return await app.send_static_file('index.html')


@app.route('/api/')
async def get_api():
    area_command = list()
    for a in available_areas.values():  # type: area.Area
        command = {
            'run (switch off)': quart.request.url_root[:-4] + 'run/' + a.name + '/0/',
            'run (Color red)': quart.request.url_root[:-4] + 'run/' + a.name + '/1/',
            'run (ColorWipe red)': quart.request.url_root[:-4] + 'run/' + a.name + '/2/',
            'run (ColorWipe blue)': quart.request.url_root[:-4] + 'run/' + a.name + '/2/0.0.255.0/',
        }
        area_command.append(command)

    return json.dumps({
        'switch_on_light': quart.request.url_root[:-4] + "switch_on/",
        'switch_off_light': quart.request.url_root[:-4] + "switch_off/",
        'strips': quart.request.url_root[:-4] + "strips/",
        'areas': quart.request.url_root[:-4] + "areas/",
        'active_calculators': quart.request.url_root[:-4] + "active_calculators/",
        'area_commands': area_command
    }), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/areas/')
async def get_areas():
    return json.dumps(list(available_areas.values()), default=convert_to_dict), 200, {
        'Content-Type': 'application/json; charset=utf-8'}


@app.route('/strips/')
async def get_strips():
    return json.dumps(list(available_strips.values()), default=convert_to_dict), 200, {
        'Content-Type': 'application/json; charset=utf-8'}


@app.route('/active_calculators/')
async def get_calculators():
    return json.dumps([(name, x.calculator) for (name, x) in available_areas.items()], default=convert_to_dict), 200, {
        'Content-Type': 'application/json; charset=utf-8'}


@app.route('/active_calculator/<name>/')
async def get_calculator(name):
    if name in available_areas:
        return json.dumps(available_areas[name],
                          default=convert_to_dict), 200, {
                   'Content-Type': 'application/json; charset=utf-8'}
    return b'Area ' + name.encode() + b' not found', 404


@app.route('/switch_on/')
async def switch_light_on():
    for light in lights_data:
        RPi.GPIO.output(light['gpio'], RPi.GPIO.HIGH)
    return json.dumps({
        'successful': True
    }), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/switch_off/')
async def switch_light_off():
    for light in lights_data:
        RPi.GPIO.output(light['gpio'], RPi.GPIO.LOW)
    return json.dumps({
        'successful': True
    }), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route('/run/<area_name>/<int:mode>/')
@app.route('/run/<area_name>/<int:mode>/<color:color1>/')
@app.route('/run/<area_name>/<int:mode>/<color:color1>/<color:color2>')
async def run_area(area_name, mode, color1: calculator.ColorRGBX = None, color2: calculator.ColorRGBX = None):
    global available_areas

    if area_name in available_areas:
        if mode > 0:
            for strip in strips_data:
                RPi.GPIO.output(strip['power_gpio'], RPi.GPIO.HIGH)
                await asyncio.sleep(1)

        a = available_areas[area_name]
        await a.set_mode(mode, color1, color2)

        if all(x.mode == 0 for x in available_areas.values()):
            for strip in strips_data:
                RPi.GPIO.output(strip['power_gpio'], RPi.GPIO.LOW)
                await asyncio.sleep(1)

        return json.dumps({
            'successful': True,
            'power': any(x.mode for x in available_areas.values())
        }), 200, {'Content-Type': 'application/json; charset=utf-8'}

    return b'Area ' + area_name.encode() + b' not found', 404


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        initialize_config()
    else:
        config_file = sys.argv[1]
        initialize_config(config_file)

    app.run(host='0.0.0.0', debug=False)
