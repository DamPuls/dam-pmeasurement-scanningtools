# -*- coding: utf-8 -*-
"""
Standalone diagnostic tool for the 3Bop motor firmware's serial link -
NOT part of the main app, run it by hand from a terminal.

Purpose: find out whether opening the serial port resets the firmware
(classic Arduino-style auto-reset via the DTR line toggling on connect),
which is what forces a physical re-home (G28) after every app restart even
though the stage never moved. See Motors_3Bop.py's connect(), which always
waits for a 'start' boot banner - a strong hint the firmware reboots on
every connect.

Sends ONLY read-only query G-codes (M114, M115) - never G28/G1/moves - so
it's safe to run at any time regardless of where the stage physically is.

Usage:
    python motor_comm_probe.py --port 10
    python motor_comm_probe.py --port 10 --scenario noreset

Scenarios:
    default  - open the serial port exactly like Motors_3Bop.connect() does
               today (baseline: expected to show the reset/boot banner).
    noreset  - open the port with DTR/RTS held low *before* the port opens,
               which on many CH340/FTDI/Arduino-clone boards suppresses the
               auto-reset pulse. If the boot banner does NOT appear here,
               the firmware likely survived the reconnect with its position
               reference intact.
    both     - run default then noreset back to back (default).

After each scenario, if no boot banner was seen, it also sends M114 to see
whether the firmware reports a real (non-homed-sentinel) position - i.e.
whether it actually remembers where it is.
"""
import argparse
import time
import serial


def _read_available(ser, duration_s):
    """Collect every line the firmware sends for duration_s seconds."""
    lines = []
    t0 = time.time()
    buf = b''
    while time.time() - t0 < duration_s:
        chunk = ser.read(ser.in_waiting or 1)
        if chunk:
            buf += chunk
            while b'\n' in buf:
                line, buf = buf.split(b'\n', 1)
                line = line.strip()
                if line:
                    lines.append(line.decode(errors='replace'))
    return lines


def _looks_like_boot_banner(lines):
    for l in lines:
        if l == 'start' or l.startswith('//') or 'BBBop_Meca' in l:
            return True
    return False


def _send_and_read(ser, cmd, duration_s=2.0):
    ser.reset_input_buffer()
    ser.write((cmd + '\n').encode())
    return _read_available(ser, duration_s)


def _send_and_wait_ok(ser, cmd, timeout=90.0):
    """Mirrors Motors_3Bop.sendCommand(): write cmd, collect lines until an
    'ok' or '!!' token, or timeout. Homing can take a while, hence the long
    default timeout - this DOES cause real motion when cmd is G28."""
    ser.reset_input_buffer()
    ser.write((cmd + '\n').encode())
    lines = []
    t0 = time.time()
    buf = b''
    while time.time() - t0 < timeout:
        chunk = ser.read(ser.in_waiting or 1)
        if chunk:
            buf += chunk
            while b'\n' in buf:
                line, buf = buf.split(b'\n', 1)
                line = line.strip().decode(errors='replace')
                if line:
                    lines.append(line)
                    token = line.split()
                    if token and token[0] in ('ok', '!!'):
                        return lines
    return lines


def run_hometest(port, baud, listen_s):
    """End-to-end test: reboot+home for real (X,Y,Z), read the resulting
    real position, close, reopen with DTR/RTS held low (no reboot) plus the
    blank-line nudge, and see whether M114 still reports that same real
    position instead of the -1,-1,-1 'unreferenced' sentinel.

    This physically moves the stage (G28 per axis) - only run with the
    bench confirmed clear/safe.
    """
    print('\n=== hometest: reboot, home X/Y/Z for real, then test a noreset reconnect ===')
    ser = serial.Serial()
    ser.port = 'COM' + str(port)
    ser.baudrate = baud
    ser.timeout = 1
    ser.open()

    boot_lines = _read_available(ser, listen_s)
    print('  boot lines: {}'.format(boot_lines or '(none)'))
    if not _looks_like_boot_banner(boot_lines):
        print('  WARNING: expected a fresh boot banner here and did not see one - '
              'homing result below may not reflect a truly clean reference.')

    for axis in ('X', 'Y', 'Z'):
        print('  homing axis {} (G28 {}) - this moves the stage, waiting for ok...'.format(axis, axis))
        lines = _send_and_wait_ok(ser, 'G28 ' + axis)
        print('    -> {}'.format(lines or '(no response / timeout)'))
        if not lines or lines[-1].split()[0] != 'ok':
            print('  ABORTING: axis {} did not cleanly return ok (got {}) - '
                  'skipping the reconnect test since the reference is unreliable.'.format(
                      axis, lines[-1] if lines else '(nothing)'))
            ser.close()
            return

    print('  querying M114 after real homing...')
    pos_after_home = _send_and_read(ser, 'M114', duration_s=2.0)
    print('  M114 response: {}'.format(pos_after_home or '(no response)'))

    ser.close()
    print('  closed the connection. Waiting 2s (simulating an app restart)...')
    time.sleep(2.0)

    print('  reopening with DTR/RTS held low (noreset method)...')
    ser2 = serial.Serial()
    ser2.port = 'COM' + str(port)
    ser2.baudrate = baud
    ser2.timeout = 1
    ser2.dtr = False
    ser2.rts = False
    ser2.dsrdtr = False
    ser2.rtscts = False
    ser2.open()

    boot_lines2 = _read_available(ser2, listen_s)
    reset_seen2 = _looks_like_boot_banner(boot_lines2)
    print('  lines seen after reopen: {}'.format(boot_lines2 or '(none)'))
    print('  => firmware {} reset on this reconnect'.format('DID' if reset_seen2 else 'did NOT'))

    _send_and_read(ser2, '', duration_s=0.5)  # blank-line nudge, as found necessary earlier
    pos_after_reconnect = _send_and_read(ser2, 'M114', duration_s=2.0)
    print('  M114 response after noreset reconnect: {}'.format(pos_after_reconnect or '(no response)'))
    ser2.close()

    print('\n  BEFORE (after real homing):        {}'.format(pos_after_home))
    print('  AFTER  (after noreset reconnect):  {}'.format(pos_after_reconnect))
    if pos_after_home and pos_after_reconnect and pos_after_home == pos_after_reconnect:
        print('  => MATCH: the firmware kept its real position reference across the noreset reconnect.')
    else:
        print('  => MISMATCH: the firmware did NOT keep its real position reference - '
              'the noreset trick alone is not enough to skip re-homing safely.')


def run_scenario(name, port, baud, listen_s, suppress_reset):
    print('\n=== scenario: {} (port=COM{}, suppress_reset_dtr_rts={}) ==='.format(
        name, port, suppress_reset))
    ser = serial.Serial()
    ser.port = 'COM' + str(port)
    ser.baudrate = baud
    ser.timeout = 1
    if suppress_reset:
        # Set DTR/RTS low *before* opening - this is the step that, on many
        # boards, prevents the reset pulse that normally happens right when
        # the port opens. dsrdtr/rtscts=False stops pyserial from touching
        # these lines again after open() on top of our explicit values.
        ser.dtr = False
        ser.rts = False
        ser.dsrdtr = False
        ser.rtscts = False
    try:
        ser.open()
    except Exception as e:
        print('  could not open {}: {}'.format(ser.port, e))
        return

    boot_lines = _read_available(ser, listen_s)
    reset_seen = _looks_like_boot_banner(boot_lines)
    print('  lines seen in first {}s after open: {}'.format(listen_s, boot_lines or '(none)'))
    print('  => firmware {} reset on this connect'.format('DID' if reset_seen else 'did NOT'))

    if not reset_seen:
        print('  no reset detected - querying M114 (current position) without any homing...')
        pos_lines = _send_and_read(ser, 'M114')
        print('  M114 response: {}'.format(pos_lines or '(no response)'))

        if any('check_Cmd_Err' in l for l in pos_lines):
            print('  got check_Cmd_Err - trying recovery attempts before giving up...')

            print('  attempt 1: blank line to nudge the parser, then M114 again')
            _send_and_read(ser, '', duration_s=0.5)
            r1 = _send_and_read(ser, 'M114')
            print('    -> {}'.format(r1 or '(no response)'))

            print('  attempt 2: M110 N0 (Marlin line-number reset), then M114')
            _send_and_read(ser, 'M110 N0', duration_s=0.5)
            r2 = _send_and_read(ser, 'M114')
            print('    -> {}'.format(r2 or '(no response)'))

            print('  attempt 3: flush input/output buffers, wait 1s, retry M114 three times')
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            time.sleep(1.0)
            for i in range(3):
                r3 = _send_and_read(ser, 'M114', duration_s=1.5)
                print('    retry {}: {}'.format(i + 1, r3 or '(no response)'))
                if r3 and not any('check_Cmd_Err' in l for l in r3):
                    break
        else:
            print('  querying M115 (firmware info) for reference...')
            info_lines = _send_and_read(ser, 'M115')
            print('  M115 response: {}'.format(info_lines or '(no response)'))

    ser.close()
    return reset_seen


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--port', type=int, required=True, help='COM port number, e.g. 10 for COM10')
    ap.add_argument('--baud', type=int, default=115200)
    ap.add_argument('--listen', type=float, default=3.0, help='seconds to watch for a boot banner after opening')
    ap.add_argument('--scenario', choices=['default', 'noreset', 'both', 'hometest'], default='both')
    args = ap.parse_args()

    if args.scenario == 'hometest':
        run_hometest(args.port, args.baud, args.listen)
    else:
        if args.scenario in ('default', 'both'):
            run_scenario('default (as the app does today)', args.port, args.baud, args.listen, suppress_reset=False)
            time.sleep(2)
        if args.scenario in ('noreset', 'both'):
            run_scenario('noreset (DTR/RTS held low before open)', args.port, args.baud, args.listen, suppress_reset=True)

        print('\nIf "noreset" showed no boot banner AND M114 returned a sane, non -1,-1,-1 '
              'position matching where the stage actually is, we can likely open the real '
              'connection the same way and skip forced re-homing on app restarts.')
