#!/usr/bin/python
# $Id:$

import random
import sys

from pyglet.gl import *
from pyglet import clock
from pyglet import font
from pyglet import window

import graphics

MAX_STREAMERS = 1000
if len(sys.argv) > 1:
    MAX_STREAMERS = int(sys.argv[1])
MAX_ADD_STREAMERS = MAX_STREAMERS // 10
MIN_STREAMER_LENGTH = 6
MAX_STREAMER_LENGTH = 20
STREAMER_SEGMENT_SIZE = 5
STREAMER_PULL_FORCE = 10
GRAVITY = -250

win = window.Window(vsync=False)
batch = graphics.Batch()
streamers = []

colors = [
    [170, 0, 0],
    [0, 255, 100],
    [80, 100, 255],
    [40, 180, 180],
    [200, 255, 100],
    [255, 70, 200],
    ]

def add_streamers():
    dx = (random.random() - .5) * win.width/4
    
    length = random.randint(MIN_STREAMER_LENGTH, MAX_STREAMER_LENGTH)
    position = []
    for i in range(length):
        if i & 1:
            position.append(win.width/2 + STREAMER_SEGMENT_SIZE - dx * i * .05)
        else:
            position.append(win.width/2 - dx * i * .05)
        position.append(-i * STREAMER_SEGMENT_SIZE/2)

    # Insert degenerate triangles at start and end
    position = position[:2] + position + position[-2:]
    length += 2

    color = random.choice(colors) * length

    streamer = batch.add(length, GL_TRIANGLE_STRIP, None, 
        ('v2f/stream', position),
        ('c3B/static', color))
    streamer.dx = dx
    streamer.dy = win.height * (.8 + random.random() * .2)
    streamer.dead = False
    streamers.append(streamer)

def update_streamers():
    global streamers
    for streamer in streamers:
        dx = streamer.dx * dt
        streamer.dy += GRAVITY * dt
        vertices = streamer.vertex_structs
        vertices[1].x += dx
        vertices[1].y += streamer.dy * dt
        for i in range(2, len(vertices) - 1):
            dy = vertices[i - 1].y - vertices[i].y
            vertices[i].x += dx
            vertices[i].y += STREAMER_PULL_FORCE * dy * dt

        # Update degenerates
        vertices[0] = vertices[1]
        vertices[-1] = vertices[-2]
        
        if vertices[-1].y <= -100:
            streamer.delete()
            streamer.dead = True
    streamers = [p for p in streamers if not p.dead]

stats_text = font.Text(font.load('', 12), '', 
                       x=win.width, y=0,
                       halign='right')

def update_stats(dt):
    np = len(streamers)
    usage = streamers[0].domain.allocator.get_usage()
    fragmentation = streamers[0].domain.allocator.get_fragmentation()
    blocks = len(streamers[0].domain.allocator.starts)
    stats_text.text = \
        'Streamers: %d  Blocks: %d  Usage: %d%%  Fragmentation: %d%%' % \
        (np, blocks, usage * 100, fragmentation * 100)
clock.schedule_interval(update_stats, 1)

fps_text = clock.ClockDisplay()

while not win.has_exit:
    win.dispatch_events()
    dt = clock.tick()
    dt = min(dt, 0.05)

    update_streamers()
    for i in range(min(MAX_ADD_STREAMERS, MAX_STREAMERS - len(streamers))):
        add_streamers()
    
    win.clear()
    batch.draw()

    stats_text.draw()
    fps_text.draw()

    win.flip()