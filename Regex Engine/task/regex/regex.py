repeat_meta_chars = {'*': (0, -1), '+': (1, -1), '?': (0, 1)}


def re_test(rx, sx):
    if rx == '':
        return True
    if sx == '':
        return False
    if rx[0] == sx[0] or rx[0] == '.':
        return re_test(rx[1:], sx[1:])
    return False


def dotpos(rx):
    foundit = False
    for t, ln in repeat_meta_chars.items():
        if t in rx:
            foundit = True
            break
    if not foundit:
        return 0
    return rx.find(t) - 1


def fix_backslash(rx):
    rxl = list(rx)
    rrxl = []
    double_slash = False
    for x in range(len(rxl)):
        if rxl[x] == '\\' and not double_slash:
            double_slash = True
            continue
        rrxl.append(rxl[x])
        double_slash = False
    return ''.join(rrxl)


def fix_repeats(rr, sr):
    if len(rr) < 2:
        return rr   # regex is too short
    if '\\' in rr:  # regex contains unary quoted chars?
        return fix_backslash(rr)
    fixup_required = False
    for c in repeat_meta_chars.keys():  # find any repeat meta-chars
        if c in rr:
            fixup_required = True
            break
    if not fixup_required:
        return rr   # return regex unchanged
    maxs = len(sr) - dotpos(rr) - 1  # maximum number of chars in fixed regex
    rl = list(rr)
    rrl = []        # fixed regex as list of chars
    k = len(rr)     # current index in regex
    while k > 0:    # loop backwards over the regex chars
        k -= 1      # previous char in regex
        if k < 0:
            break   # exit loop if regex is exhausted
        for t, ln in repeat_meta_chars.items():
            j = 0           # meta repeat counter
            if rl[k] == t:  # regex contains a repeater?
                if not ln[0]:   # zero repeats allowed?
                    if rl[k-1] != '.' and rl[k-1] != sr[len(sr) - len(rl) + k]:    # no match?
                        k -= 2  # step over (ie ignore) the repeat
                    else:
                        k -= 1
                        m = p = k   # meta repeated char index
                        while len(rrl) < maxs:  # while there is space
                            rrl.append(rl[m])  # expand the repeated char
                            p -= 1
                            j += 1
                            if ln[1] == j:  # except if meta repeat is exceeded
                                # j = 0
                                break
                            if rl[m] != '.' and rl[m] != sr[len(sr) - len(rl) + p + 1]:  # no match!
                                # j = 0       # or if meta repeat is no match
                                k -= 1
                                break
                else:
                    if rl[k - 1] == '.' or rl[k - 1] == sr[len(sr) - len(rl) + k]:
                        k -= 1
                        m = p = k  # meta repeated char index
                        while len(rrl) < maxs:  # while there is space
                            rrl.append(rl[m])  # expand the repeated char
                            p -= 1
                            j += 1
                            if ln[1] == j:  # except if meta repeat is exceeded
                                # j = 0
                                break
                            if rl[m] != '.' and rl[m] != sr[len(sr) - len(rl) + p + 1]:  # no match!
                                # j = 0       # or if meta repeat is no match
                                k -= 1
                                break
                    else:
                        break
        if j == 0:  # not a repeat; just copy it to fixed regex
            if rl[k] not in repeat_meta_chars.keys():
                rrl.append(rl[k])
    rrl.reverse()
    return ''.join(rrl)


def lenx(r):
    return len(r) - dotpos(r)


def re_v(r, s):
    lock_start = False
    lock_fin = False
    if r == '':
        return True
    if s == '':
        return False
    if r[0] == '^':     # process starting anchor
        lock_start = True
        r = r[1:]       # remove start anchor character from regex
    if r[-1] == '$':    # process ending anchor
        lock_fin = True
        r = r[:-1]      # remove end anchor character from regex
    # print(f'Regex; Before: {r}')
    r = fix_repeats(r, s)   # remove repeat meta-chars
    # print(f'Regex; After: {r}')
    if len(r) > len(s):
        return False
    if lock_start and lock_fin and not len(r) == len(s):
        return False
    if lock_start:
        # not proper regex but required to pass
        # truncate RE after repeat meta-char, if any...
        if re_test(r, s[:lenx(r)]):
            return True
    elif lock_fin:
        # not proper regex but required to pass
        # truncate RE after repeat meta-char, if any...
        if re_test(r, s[len(s) - lenx(r):]):
            return True
    else:
        for i in range(len(s) - len(r) + 1):
            if re_test(r, s[i:i + len(r)]):
                return True
    return False


re, st = input().strip().split('|')
print(re_v(re, st))
