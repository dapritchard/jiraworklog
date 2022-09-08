#!/usr/bin/env python3

from datetime import timedelta
from jiraworklog.update_instructions import UpdateInstructions, calc_issue_max_strwidth, calc_n_updates, strptime_ptl


def unconditional_updates(_: UpdateInstructions) -> None:
    pass


def confirm_updates(
    update_instrs: UpdateInstructions,
    is_dry_run: bool
) -> None:
    if is_dry_run:
        confirm_updates_dryrun_yes(update_instrs)
    else:
        confirm_updates_dryrun_no(update_instrs)


def confirm_updates_dryrun_no(update_instrs: UpdateInstructions) -> None:
    n_updates = calc_n_updates(update_instrs)
    if n_updates == 0:
        print('There are no changes to be made')
        return
    print('\nThe following changes will be made')
    print(fmt_changes(update_instrs))
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


def confirm_updates_dryrun_yes(update_instrs: UpdateInstructions) -> None:
    n_updates = calc_n_updates(update_instrs)
    if n_updates == 0:
        print('Dry run. There are no changes to be made')
        return
    print('\nDry run. The following changes would be made')
    print(fmt_changes(update_instrs))


def fmt_changes(update_instr: UpdateInstructions) -> str:

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
    changes = ['']
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
    return '\n'.join(changes)
