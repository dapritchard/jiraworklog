#!/usr/bin/env python3

import argparse
from datetime import timedelta
from jiraworklog.update_instructions import UpdateInstructions, calc_issue_max_strwidth, calc_n_updates, strptime_ptl


def unconditional_updates(_: UpdateInstructions) -> None:
    pass


def confirm_updates(
    update_instrs: UpdateInstructions,
    cmdline_args: argparse.Namespace
) -> None:
    update_msgs = fmt_updates(update_instrs, cmdline_args)
    print('\n'.join(update_msgs))
    is_noconfirm = (
        cmdline_args.dry_run
        or cmdline_args.auto_confirm
        or calc_n_updates(update_instrs) == 0
    )
    if not is_noconfirm:
        print('Do you want to proceed with the updates? [y/n]: ', end='')
        while True:
            response = input()
            if response == 'y':
                return
            elif response == 'n':
                raise RuntimeError('User specified exit')
            msg = (
                f"Invalid response '{response}'. Do you want to proceed with the "
                'updates? [y/n]: '
            )
            print(msg, end='')


def fmt_updates(
    update_instrs: UpdateInstructions,
    cmdline_args: argparse.Namespace
) -> list[str]:

    # TODO: maybe --auto-confirm has the same message as "regular" mode?
    if cmdline_args.auto_confirm:
        header_fragm = 'Auto-confirm. '
        changes_fragm = 'The following changes will be made.'
    elif cmdline_args.dry_run:
        header_fragm = 'Dry run. '
        changes_fragm = 'The following changes would be made.'
    else:
        header_fragm = ''
        changes_fragm = 'The following changes will be made.'

    n_updates = calc_n_updates(update_instrs)
    if n_updates == 0:
        update_msgs = [f'{header_fragm}There are no changes to be made']
    else:
        update_msgs = [
            '',
            f'{header_fragm}{changes_fragm}',
            ''
        ]
        update_msgs.extend(fmt_changes(update_instrs))

    return update_msgs


def fmt_changes(update_instr: UpdateInstructions) -> list[str]:

    def add_padding(s: str, w: int) -> str:
        padding = ' ' * (w - len(s))
        return s + padding

    def to_timediff(s: str) -> timedelta:
        return timedelta(seconds = int(s))

    def fmt_duration(seconds: str) -> str:
        """We give 4 spaces of padding whenever the width of `h` is 1, and take 1
        space away for each additional digit in `h`."""
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if s >= 30:
            if m == 59:
                h = h + 1
                m = 0
            else:
                m = m + 1
        duration = f"({h}:{str(m) if m >= 10 else '0' + str(m)})"
        pad = ' ' * (10 - len(duration))
        return pad + duration

    def fmt_worklogs(listwkls, pad):
        lines_map = {}
        date_fmt = {}
        for x in listwkls:
            padkey = pad(x.issueKey)
            started_dt = strptime_ptl(x.canon['started'])
            ended_dt = started_dt + to_timediff(x.canon['timeSpentSeconds'])
            padded_dur = fmt_duration(x.canon['timeSpentSeconds'])
            date = started_dt.strftime('%Y-%m-%d')
            day = started_dt.strftime('%A %B %d, %Y')
            started = started_dt.strftime('%H:%M')
            ended = ended_dt.strftime('%H:%M')
            line = f"    {padkey}    {started}-{ended}{padded_dur}    {x.canon['comment']}"
            if date in lines_map:
                lines_map[date].append(line)
            else:
                lines_map[date] = [line]
                date_fmt[date] = day
        lines = []
        for k in sorted(lines_map.keys()):
            lines.append(date_fmt[k])
            lines.extend(lines_map[k])
        return lines

    issue_max_strwidth = calc_issue_max_strwidth(update_instr)
    pad = lambda x: add_padding(x, issue_max_strwidth)
    fmt_worklogs_ptl = lambda x: fmt_worklogs(x, pad)
    changes = []
    if len(update_instr.chk_add_listwkl) >= 1:
        changes.append('-- Add to checked-in worklogs only -------------------------')
        changes.extend(fmt_worklogs_ptl(update_instr.chk_add_listwkl))
        changes.append('')
    if len(update_instr.chk_remove_listwkl) >= 1:
        changes.append('-- Remove from checked-in worklogs only --------------------')
        changes.extend(fmt_worklogs_ptl(update_instr.chk_remove_listwkl))
        changes.append('')
    if len(update_instr.rmt_add_listwkl) >= 1:
        changes.append('-- Add to remote worklogs ----------------------------------'),
        changes.extend(fmt_worklogs_ptl(update_instr.rmt_add_listwkl))
        changes.append('')
    if len(update_instr.rmt_remove_listwkl) >= 1:
        changes.append('-- Remove from remote worklogs -----------------------------')
        changes.extend(fmt_worklogs_ptl(update_instr.rmt_remove_listwkl))
        changes.append('')

    return changes
