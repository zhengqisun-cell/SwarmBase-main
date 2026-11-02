#!/usr/bin/env python3
"""Read-only test of JoystickManager; imports no serial, robot control or motor modules."""
import os
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS', '1')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
import tkinter as tk
from tkinter import ttk
import pygame
from pygame._sdl2 import controller
from input.JoystickManager import JoystickManager
try:
    from input.JoystickManager import AXES as RAW
except ImportError:  # JoystickManager without per-OS axes: Linux numbers
    RAW = dict(left_horz=0, left_vert=1, left_trigger=2, right_horz=3, right_vert=4, right_trigger=5)

LOG_DIR = Path(__file__).resolve().parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)
OUTPUT = LOG_DIR / 'xbox-controller-mapping-test.json'
EVENTS = LOG_DIR / 'xbox-controller-input-events.jsonl'
# Output order of getJoysticks() and getButtons(); raw axis numbers as JoystickManager picks them for this OS.
AXES = [('Left stick up/down', RAW['left_vert']), ('Left stick left/right', RAW['left_horz']),
        ('Right stick up/down', RAW['right_vert']), ('Right stick left/right', RAW['right_horz']),
        ('Left trigger LT', RAW['left_trigger']), ('Right trigger RT', RAW['right_trigger'])]
BUTTONS = [('A', 0), ('B', 1), ('X', 2), ('Y', 3), ('Left bumper LB', 4), ('Right bumper RB', 5)]
STEPS = [
    ('Left stick left/right: push fully left, then fully right, then release to center', 'axis', RAW['left_horz'], True),
    ('Left stick up/down: push fully up, then fully down, then release to center', 'axis', RAW['left_vert'], True),
    ('Right stick left/right: push fully left, then fully right, then release to center', 'axis', RAW['right_horz'], True),
    ('Right stick up/down: push fully up, then fully down, then release to center', 'axis', RAW['right_vert'], True),
    ('Left trigger LT: press all the way, then release fully', 'trigger', RAW['left_trigger'], True),
    ('Right trigger RT: press all the way, then release fully', 'trigger', RAW['right_trigger'], True),
] + [(f'Press {name} once and release', 'button', index, True) for name, index in BUTTONS] + [
    ('Press View (two-windows button) once and release', 'button', 6, False),
    ('Press Menu (three-lines button) once and release', 'button', 7, False),
    ('Press the left stick L3 and release', 'button', 9, False),
    ('Press the right stick R3 and release', 'button', 10, False),
    ('D-pad: press up, down, left and right once each, then release', 'hat', 0, False),
    ('Press the Xbox button once and release (skip if the system intercepts it)', 'button', 8, False),
]

pygame.init()
pygame.joystick.init()
controller.init()
devices = []
for i in range(pygame.joystick.get_count()):
    j = pygame.joystick.Joystick(i)
    devices.append({'index': i, 'name': j.get_name(), 'guid': j.get_guid()})
candidates = [d for d in devices if 'xbox' in d['name'].lower() or 'x-box' in d['name'].lower()]
if len(candidates) != 1:
    raise SystemExit('Connect exactly one recognizable Xbox controller: ' + json.dumps(devices, ensure_ascii=False))
selected = candidates[0]
manager = JoystickManager(selected['index'])
joystick = manager.joystick
instance_id = joystick.get_instance_id()
assert joystick.get_numaxes() >= 6 and joystick.get_numbuttons() >= 6
standard = controller.Controller(selected['index']) if controller.is_controller(selected['index']) else None
metadata = {**selected, 'instance_id': instance_id, 'axes_count': joystick.get_numaxes(),
            'buttons_count': joystick.get_numbuttons(), 'hats_count': joystick.get_numhats(),
            'pygame_version': pygame.version.ver, 'sdl_mapping': standard.get_mapping() if standard else None,
            'original_axis_indices': [i for _, i in AXES],
            'original_button_indices': [i for _, i in BUTTONS]}
report = {'started_at_utc': datetime.now(timezone.utc).isoformat(), 'read_only': True,
          'robot_serial_opened': False, 'robot_commands_sent': 0,
          'uses_original_joystick_manager': True, 'device': metadata, 'results': []}
print('DEVICE', json.dumps(metadata, ensure_ascii=False), flush=True)

window = tk.Tk()
window.tk.call('tk', 'scaling', 1.25)
style = ttk.Style(window)
style.configure('Treeview', rowheight=28, font=('Noto Sans CJK SC', -14))
style.configure('Treeview.Heading', font=('Noto Sans CJK SC', -14, 'bold'))
window.title('Xbox controller read-only mapping test - no base station, no motor control')
window.geometry('1120x880+120+90')
window.option_add('*Font', ('Noto Sans CJK SC', -14))
frame = ttk.Frame(window, padding=16)
frame.pack(fill='both', expand=True)
ttk.Label(frame, text='Read-only input test: JoystickManager', font=('Noto Sans CJK SC', -20, 'bold')).pack(anchor='w')
ttk.Label(frame, text=f"Device: {selected['name']}   Pygame index: {selected['index']}   No robot serial port opened").pack(anchor='w', pady=(4, 10))
instruction = tk.StringVar(value='Release all sticks, triggers and buttons first; recording the initial state...')
ttk.Label(frame, textvariable=instruction, foreground='#1565c0', font=('Noto Sans CJK SC', -17), wraplength=1070).pack(anchor='w', pady=8)
values_view = ttk.Treeview(frame, columns=('index', 'name', 'raw', 'value'), show='headings', height=6)
for c, title, width in [('index', 'Project output', 150), ('name', 'Physical input', 300), ('raw', 'Raw axis', 180), ('value', 'Current value', 200)]:
    values_view.heading(c, text=title); values_view.column(c, width=width, anchor='center')
for i, (name, axis) in enumerate(AXES):
    values_view.insert('', 'end', iid=str(i), values=(f'axis[{i}]', name, f'axis {axis}', '-'))
values_view.pack(fill='x', pady=8)
button_text = tk.StringVar()
ttk.Label(frame, textvariable=button_text, wraplength=1070).pack(anchor='w', pady=8)
status = tk.StringVar(value='Initializing; this window only reads the controller and sends no flight commands.')
ttk.Label(frame, textvariable=status, wraplength=1070).pack(anchor='w', pady=4)
results_view = ttk.Treeview(frame, columns=('step', 'item', 'result'), show='headings', height=15)
for c, title, width in [('step', 'No.', 60), ('item', 'Test item', 690), ('result', 'Result', 270)]:
    results_view.heading(c, text=title); results_view.column(c, width=width)
results_view.pack(fill='both', expand=True, pady=8)
controls = ttk.Frame(frame); controls.pack(fill='x')
state = {'step': 0, 'ready_at': time.monotonic()+2, 'min': [1.0]*joystick.get_numaxes(),
         'max': [-1.0]*joystick.get_numaxes(), 'stable': 0, 'pressed': None, 'hats': set(),
         'events': 0, 'finished': False, 'last_save': 0, 'connected': True}
review = '--review' in sys.argv
if review:
    saved = json.loads(OUTPUT.read_text())
    if saved.get('device', {}).get('guid') != metadata['guid'] or not saved.get('all_steps_finished'):
        raise SystemExit('The saved result is not a complete test of this controller; start without --review.')
    report = saved
    state.update(step=len(STEPS), finished=True, events=report.get('event_count', 0))
    for item in report['results']:
        results_view.insert('', 'end', values=(item['step'], item['instruction'], 'Pass' if item['passed'] else 'Check'))
    instruction.set('Test finished. All 18 results are saved; you can keep watching the controller input (read-only).')
event_stream = EVENTS.open('a' if review else 'w', buffering=1)

def save():
    report['updated_at_utc'] = datetime.now(timezone.utc).isoformat()
    report['all_steps_finished'] = state['finished']
    core = [r for r in report['results'] if r['required']]
    report['original_mapping_tests_complete'] = len(core) == 12
    report['original_mapping_tests_passed'] = len(core) == 12 and all(r['passed'] for r in core)
    report['selected_device_connected'] = state['connected']
    report['event_count'] = state['events']
    report['last_raw_axes'] = [joystick.get_axis(i) for i in range(joystick.get_numaxes())] if state['connected'] else None
    temporary = OUTPUT.with_suffix('.tmp')
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    temporary.replace(OUTPUT)

def finish_step(passed, details):
    n = state['step']
    label, kind, index, required = STEPS[n]
    result = {'step': n+1, 'instruction': label, 'kind': kind, 'expected_raw_index': index,
              'required': required, 'passed': passed, **details}
    report['results'].append(result)
    results_view.insert('', 'end', values=(n+1, label, 'Pass' if passed else ('Skipped' if details.get('skipped') else 'Check')))
    results_view.yview_moveto(1)
    print('STEP_RESULT', json.dumps(result, ensure_ascii=False), flush=True)
    state.update(step=n+1, min=[1.0]*joystick.get_numaxes(), max=[-1.0]*joystick.get_numaxes(),
                 stable=0, pressed=None, hats=set(), ready_at=time.monotonic()+0.9)
    if state['step'] == len(STEPS):
        state['finished'] = True
        instruction.set('Test finished. The mapping results are saved; keep using the controller to watch the values.')
    save()

def skip():
    if not state['finished']: finish_step(False, {'skipped': True})

def reset():
    report['results'] = []
    for item in results_view.get_children(): results_view.delete(item)
    state.update(step=0, ready_at=time.monotonic()+2, min=[1.0]*joystick.get_numaxes(),
                 max=[-1.0]*joystick.get_numaxes(), stable=0, pressed=None, hats=set(), finished=False)
    instruction.set('Release all inputs; restarting in 2 s.')
    save()

def close():
    save();event_stream.close();pygame.quit();window.destroy()

ttk.Button(controls, text='Restart test', command=reset).pack(side='left', padx=4)
ttk.Button(controls, text='Skip current item (recorded as not passed)', command=skip).pack(side='left', padx=4)
ttk.Button(controls, text='Save and close', command=close).pack(side='right', padx=4)
window.protocol('WM_DELETE_WINDOW', close)

def tick():
    try:
        if not joystick.get_init(): raise RuntimeError('Controller disconnected')
        axes, buttons = manager.getJoystickInputs()
        events = pygame.event.get()
        for event in events:
            if getattr(event, 'instance_id', None) != instance_id: continue
            if event.type not in [pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYHATMOTION]: continue
            state['events'] += 1
            event_stream.write(json.dumps({'t': time.monotonic(), 'type': pygame.event.event_name(event.type), **event.dict})+'\n')
        if standard and not standard.attached(): raise RuntimeError('Controller disconnected')
        raw = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
        hats = [joystick.get_hat(i) for i in range(joystick.get_numhats())]
        for i, value in enumerate(axes):
            name, index = AXES[i]
            values_view.item(str(i), values=(f'axis[{i}]', name, f'axis {index}', f'{value:+.4f}'))
        pressed = [str(i) for i in range(joystick.get_numbuttons()) if joystick.get_button(i)]
        button_text.set('Project buttons: '+'   '.join(f'{name}[{index}]={buttons[i]}' for i,(name,index) in enumerate(BUTTONS))
                        +'\nAll pressed raw buttons: '+(', '.join(pressed) or 'none')+f'   D-pad: {hats}')
        now = time.monotonic()
        if now >= state['ready_at'] and not state['finished']:
            label, kind, index, required = STEPS[state['step']]
            instruction.set(f"Item {state['step']+1}/{len(STEPS)}: {label}")
            for i,v in enumerate(raw):
                state['min'][i]=min(state['min'][i],v);state['max'][i]=max(state['max'][i],v)
            if kind in ['axis','trigger']:
                lo,hi,current=state['min'][index],state['max'][index],raw[index]
                returned = abs(current)<0.12 if kind=='axis' else current < -0.85
                full_range = lo < -0.85 and hi > 0.85
                state['stable'] = state['stable']+1 if full_range and returned else 0
                status.set(f'Raw axis {index}: min {lo:+.3f}, max {hi:+.3f}, current {current:+.3f}; cover both ends, then release.')
                if state['stable'] >= 5:
                    finish_step(True, {'minimum':lo,'maximum':hi,'released_value':current})
            elif kind=='button':
                for event in events:
                    if getattr(event,'instance_id',None)!=instance_id:continue
                    if event.type==pygame.JOYBUTTONDOWN and state['pressed'] is None:state['pressed']=event.button
                    elif event.type==pygame.JOYBUTTONUP and event.button==state['pressed']:
                        finish_step(event.button==index, {'observed_raw_index':event.button});break
                status.set(f'Expecting raw button {index}; pressed now: '+(', '.join(pressed) or 'none'))
            else:
                if hats:
                    state['hats'].add(hats[index])
                    status.set('Directions seen: '+str(sorted(state['hats'])))
                    if {(0,1),(0,-1),(-1,0),(1,0)} <= state['hats'] and hats[index]==(0,0):
                        finish_step(True, {'observed_directions':sorted(state['hats'])})
        if state['finished']:
            status.set('Core 12 items: '+('all passed' if report.get('original_mapping_tests_passed') else 'some incomplete or need checking')+'; window stays read-only.')
        if now-state['last_save']>0.5:
            state['last_save']=now;save()
    except (pygame.error, RuntimeError) as exc:
        state['connected']=False;status.set('Reading stopped: '+str(exc));save()
        print('INPUT_ERROR',str(exc),flush=True)
        return
    window.after(20,tick)

save()
window.after(20,tick)
window.update_idletasks()
print(f'GUI_WINDOW_ID=0x{window.winfo_id():x}',flush=True)
window.mainloop()
