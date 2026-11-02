#!/usr/bin/env python3
"""只读测试原 JoystickManager；不导入串口、机器人控制或电机模块。"""
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

OUTPUT = Path('/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/outputs/Xbox-controller-mapping-test.json')
EVENTS = Path('/home/zhengqi-sun/Documents/Codex/2026-10-15/codex/work/xbox-input-test/input-events.jsonl')
# 原项目 getJoysticks() 和 getButtons() 的输出顺序，不改变映射。
AXES = [('左摇杆上下', 1), ('左摇杆左右', 0), ('右摇杆上下', 4),
        ('右摇杆左右', 3), ('左扳机 LT', 2), ('右扳机 RT', 5)]
BUTTONS = [('A', 0), ('B', 1), ('X', 2), ('Y', 3), ('左肩键 LB', 4), ('右肩键 RB', 5)]
STEPS = [
    ('左摇杆左右：先推到最左，再到最右，最后松手归中', 'axis', 0, True),
    ('左摇杆上下：先推到最上，再到最下，最后松手归中', 'axis', 1, True),
    ('右摇杆左右：先推到最左，再到最右，最后松手归中', 'axis', 3, True),
    ('右摇杆上下：先推到最上，再到最下，最后松手归中', 'axis', 4, True),
    ('左扳机 LT：完全按到底，再完全松开', 'trigger', 2, True),
    ('右扳机 RT：完全按到底，再完全松开', 'trigger', 5, True),
] + [(f'按一下 {name}，再松开', 'button', index, True) for name, index in BUTTONS] + [
    ('按一下 View／双窗口键，再松开', 'button', 6, False),
    ('按一下 Menu／三横线键，再松开', 'button', 7, False),
    ('按下左摇杆 L3，再松开', 'button', 9, False),
    ('按下右摇杆 R3，再松开', 'button', 10, False),
    ('十字方向键：上下左右各按一次，最后松开', 'hat', 0, False),
    ('按一下 Xbox／西瓜键，再松开（系统拦截时可跳过）', 'button', 8, False),
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
    raise SystemExit('需连接一只可明确识别的 Xbox 手柄：' + json.dumps(devices, ensure_ascii=False))
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
window.title('Xbox 手柄只读映射测试 — 不连接基站、不控制电机')
window.geometry('1120x880+120+90')
window.option_add('*Font', ('Noto Sans CJK SC', -14))
frame = ttk.Frame(window, padding=16)
frame.pack(fill='both', expand=True)
ttk.Label(frame, text='只读输入测试：原项目 JoystickManager', font=('Noto Sans CJK SC', -20, 'bold')).pack(anchor='w')
ttk.Label(frame, text=f"设备：{selected['name']}　Pygame 序号：{selected['index']}　未打开任何机器人串口").pack(anchor='w', pady=(4, 10))
instruction = tk.StringVar(value='请先完全松开摇杆、扳机和按键，正在记录初始状态……')
ttk.Label(frame, textvariable=instruction, foreground='#1565c0', font=('Noto Sans CJK SC', -17), wraplength=1070).pack(anchor='w', pady=8)
values_view = ttk.Treeview(frame, columns=('index', 'name', 'raw', 'value'), show='headings', height=6)
for c, title, width in [('index', '原项目输出', 150), ('name', '物理输入', 300), ('raw', '原始轴编号', 180), ('value', '当前读数', 200)]:
    values_view.heading(c, text=title); values_view.column(c, width=width, anchor='center')
for i, (name, axis) in enumerate(AXES):
    values_view.insert('', 'end', iid=str(i), values=(f'axis[{i}]', name, f'axis {axis}', '—'))
values_view.pack(fill='x', pady=8)
button_text = tk.StringVar()
ttk.Label(frame, textvariable=button_text, wraplength=1070).pack(anchor='w', pady=8)
status = tk.StringVar(value='正在初始化；此窗口只读取手柄，不发送任何飞行指令。')
ttk.Label(frame, textvariable=status, wraplength=1070).pack(anchor='w', pady=4)
results_view = ttk.Treeview(frame, columns=('step', 'item', 'result'), show='headings', height=15)
for c, title, width in [('step', '序号', 60), ('item', '测试项', 690), ('result', '结果', 270)]:
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
        raise SystemExit('已保存结果不是当前手柄的完整测试，请不带 --review 启动。')
    report = saved
    state.update(step=len(STEPS), finished=True, events=report.get('event_count', 0))
    for item in report['results']:
        results_view.insert('', 'end', values=(item['step'], item['instruction'], '通过' if item['passed'] else '需核对'))
    instruction.set('测试结束。18 项结果已保存；可以继续只读查看手柄输入。')
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
    results_view.insert('', 'end', values=(n+1, label, '通过' if passed else ('跳过' if details.get('skipped') else '需核对')))
    results_view.yview_moveto(1)
    print('STEP_RESULT', json.dumps(result, ensure_ascii=False), flush=True)
    state.update(step=n+1, min=[1.0]*joystick.get_numaxes(), max=[-1.0]*joystick.get_numaxes(),
                 stable=0, pressed=None, hats=set(), ready_at=time.monotonic()+0.9)
    if state['step'] == len(STEPS):
        state['finished'] = True
        instruction.set('测试结束。原项目映射结果已保存，可继续操作手柄观察读数。')
    save()

def skip():
    if not state['finished']: finish_step(False, {'skipped': True})

def reset():
    report['results'] = []
    for item in results_view.get_children(): results_view.delete(item)
    state.update(step=0, ready_at=time.monotonic()+2, min=[1.0]*joystick.get_numaxes(),
                 max=[-1.0]*joystick.get_numaxes(), stable=0, pressed=None, hats=set(), finished=False)
    instruction.set('请先松开所有输入，2 秒后重新开始。')
    save()

def close():
    save();event_stream.close();pygame.quit();window.destroy()

ttk.Button(controls, text='重新测试', command=reset).pack(side='left', padx=4)
ttk.Button(controls, text='跳过当前项（会如实记录未通过）', command=skip).pack(side='left', padx=4)
ttk.Button(controls, text='关闭并保存', command=close).pack(side='right', padx=4)
window.protocol('WM_DELETE_WINDOW', close)

def tick():
    try:
        if not joystick.get_init(): raise RuntimeError('手柄已断开')
        axes, buttons = manager.getJoystickInputs()
        events = pygame.event.get()
        for event in events:
            if getattr(event, 'instance_id', None) != instance_id: continue
            if event.type not in [pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYHATMOTION]: continue
            state['events'] += 1
            event_stream.write(json.dumps({'t': time.monotonic(), 'type': pygame.event.event_name(event.type), **event.dict})+'\n')
        if standard and not standard.attached(): raise RuntimeError('手柄已断开')
        raw = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
        hats = [joystick.get_hat(i) for i in range(joystick.get_numhats())]
        for i, value in enumerate(axes):
            name, index = AXES[i]
            values_view.item(str(i), values=(f'axis[{i}]', name, f'axis {index}', f'{value:+.4f}'))
        pressed = [str(i) for i in range(joystick.get_numbuttons()) if joystick.get_button(i)]
        button_text.set('原项目按键：'+'　'.join(f'{name}[{index}]={buttons[i]}' for i,(name,index) in enumerate(BUTTONS))
                        +'\n全部按下的原始编号：'+(', '.join(pressed) or '无')+f'　十字键：{hats}')
        now = time.monotonic()
        if now >= state['ready_at'] and not state['finished']:
            label, kind, index, required = STEPS[state['step']]
            instruction.set(f"第 {state['step']+1}/{len(STEPS)} 项：{label}")
            for i,v in enumerate(raw):
                state['min'][i]=min(state['min'][i],v);state['max'][i]=max(state['max'][i],v)
            if kind in ['axis','trigger']:
                lo,hi,current=state['min'][index],state['max'][index],raw[index]
                returned = abs(current)<0.12 if kind=='axis' else current < -0.85
                full_range = lo < -0.85 and hi > 0.85
                state['stable'] = state['stable']+1 if full_range and returned else 0
                status.set(f'原始轴 {index}：最小 {lo:+.3f}，最大 {hi:+.3f}，当前 {current:+.3f}；需覆盖两端并松手。')
                if state['stable'] >= 5:
                    finish_step(True, {'minimum':lo,'maximum':hi,'released_value':current})
            elif kind=='button':
                for event in events:
                    if getattr(event,'instance_id',None)!=instance_id:continue
                    if event.type==pygame.JOYBUTTONDOWN and state['pressed'] is None:state['pressed']=event.button
                    elif event.type==pygame.JOYBUTTONUP and event.button==state['pressed']:
                        finish_step(event.button==index, {'observed_raw_index':event.button});break
                status.set(f'期待原始按键 {index}；当前按下：'+(', '.join(pressed) or '无'))
            else:
                if hats:
                    state['hats'].add(hats[index])
                    status.set('已观察到方向：'+str(sorted(state['hats'])))
                    if {(0,1),(0,-1),(-1,0),(1,0)} <= state['hats'] and hats[index]==(0,0):
                        finish_step(True, {'observed_directions':sorted(state['hats'])})
        if state['finished']:
            status.set('原项目核心 12 项：'+('全部通过' if report.get('original_mapping_tests_passed') else '有未完成或需核对项')+'；窗口保持只读。')
        if now-state['last_save']>0.5:
            state['last_save']=now;save()
    except (pygame.error, RuntimeError) as exc:
        state['connected']=False;status.set('读取停止：'+str(exc));save()
        print('INPUT_ERROR',str(exc),flush=True)
        return
    window.after(20,tick)

save()
window.after(20,tick)
window.update_idletasks()
print(f'GUI_WINDOW_ID=0x{window.winfo_id():x}',flush=True)
window.mainloop()
