# Midi Controller for the Adafruit Macropad RP2040. Setup the MAcropad to use midi RX and TX through the STEMMA QT port 

import time
import board, busio, keypad, rotaryio, neopixel
import displayio, terminalio
import usb_midi
import audiocore, audiomixer, audiopwmio
from adafruit_display_text import bitmap_label as label
#from adafruit_ticks import ticks_ms, ticks_diff, ticks_add
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

# --- Key variables ---
key_pins = (board.KEY1, board.KEY2, board.KEY3,
            board.KEY4, board.KEY5, board.KEY6,
            board.KEY7, board.KEY8, board.KEY9,
            board.KEY10, board.KEY11, board.KEY12)
keys = keypad.Keys(key_pins, value_when_pressed=False, pull=True)

midi_notes = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79]


# --- MIDI variables ---
uart = busio.UART(tx=board.SDA, rx=board.SCL, baudrate=31250, timeout=0.001)
midi = adafruit_midi.MIDI(midi_in=uart, midi_out=uart, debug=False)

leds = neopixel.NeoPixel(board.NEOPIXEL, 12, brightness=0.3, auto_write=False)

encoder = rotaryio.IncrementalEncoder(board.ENCODER_B, board.ENCODER_A)  # yes, reversed
encoder_switch = keypad.Keys((board.ENCODER_SWITCH,), value_when_pressed=False, pull=True)
last_encoder_value = 0

keys_pressed = [False] * 12
last_key_time = time.monotonic()

def trigger_note(kind,note,vel):
    # send on channel equal to the     
    n = note % 12
    keys_pressed[n] = True if vel > 0 else False
    print(f"{kind} {note} {vel}")
    leds[n] = (0, 0, vel)
    leds.show()
    midi.send(NoteOn(note, vel))

def midi_receive():
    msg = midi.receive()
    if msg is not None and msg._STATUS == 0x90:
        print(time.monotonic(), msg)
        # if isinstance(msg, NoteOn) and msg.velocity:
        #     print("noteOn:",msg.note, msg.note % 12)
        #     trigger_note('m', msg.note,msg.velocity)
        # if isinstance(msg,NoteOff) or (isinstance(msg, NoteOn) and msg.velocity==0):
        #     trigger_note('m', msg.note,0)

def encoder_switch_pressed():
    return encoder_switch.events.get() is not None

def encoder_switch_released():
    return encoder_switch.events.get() is not None

def encoder_switch_value():
    return encoder_switch.events.get().pressed

def encoder_value():
    # make encoder_last_value global
    global last_encoder_value
    if encoder.position == 0 or encoder.position == 13 or encoder.position < 0:
        # reset encoder value to 0
        encoder.position = 0
        return 0
    if encoder.position != last_encoder_value:
        last_encoder_value = encoder.position
        print("encoder:", encoder.position)
    return encoder.position % 12

def encoder_value_changed():
    return encoder.position != 0

def encoder_value_reset():
    encoder.position = 0

def encoder_value_set(value):
    encoder.position = value

# --- Main loop ---
while True:
    midi_receive()
    # get the encoder value
    enc = encoder_value()
     # Key handling
    key = keys.events.get()
    if key == None:
        continue   # no keys? go back to while

    # only pressed / released key logic beyond this point

    # otherwise key was pressed or released
    keynum = key.key_number
    print("key!",keynum, key.pressed)

    if key.pressed:
        trigger_note('k', keynum, 127)

    if key.released:
        trigger_note('k', keynum, 0)

    