#!/usr/bin/env python3


from datetime import timedelta
from jiraworklog.update_instructions import UpdateInstructions, calc_issue_max_strwidth, calc_n_updates, strptime_ptl


def unconditional_updates(_: UpdateInstructions) -> None:
    pass


def confirm_updates(update_instrs: UpdateInstructions) -> None:
    n_updates = calc_n_updates(update_instrs)
    if n_updates == 0:
        print('There are no changes to be made\n')
        return
    print('The following changes will be made')
    print(fmt_changes(update_instrs))
    print('Do you want to proceed with the updates? [y/n]:  ')
    while True:
        response = input()
        if response == 'y':
            return
        elif response == 'n':
            raise RuntimeError('User specified exit')
        msg = (
            f"Invalid response '{response}'. Do you want to proceed with the "
            'updates? [y/n]:  '
        )
        print(msg)


def fmt_changes(update_instr: UpdateInstructions) -> str:

    def add_padding(s: str, w: int) -> str:
        padding = ' ' * (w - len(s))
        return s + padding

    def to_timediff(s: str) -> timedelta:
        return timedelta(seconds = int(s))

    def fmt_worklogs(listwkls, pad):
        lines = []
        for x in listwkls:
            padkey = pad(f'{x.issueKey}:')
            started_dt = strptime_ptl(x.canon['started'])
            ended_dt = started_dt + to_timediff(x.canon['timeSpentSeconds'])
            started = started_dt.strftime('%Y-%m-%dT%H:%M')
            ended = ended_dt.strftime('%Y-%m-%dT%H:%M')
            line = f"{padkey}  {started}  {ended}  {x.canon['comment']}"
            lines.append(line)
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
