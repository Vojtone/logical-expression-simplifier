"""
- not w wyrażeniu jako '~' i nie działa poprawnie za każdym razem
- zmienne wyłącznie jednoliterowe (małe)
- nie ma obsługi '=='
"""
from collections import defaultdict
import string
VARS = string.ascii_lowercase + '0' + '1'
OPS = ["|", "&", ">", "^"]

"""
#do zmiennych wieloliterowych
from keyword import iskeyword
'not'.isidentifier() & (not iskeyword('not'))
"""

def check_if_valid(expr):

    n = 0
    state = 0
    vars_set = set();
    """
        1 - (
        2 - )
        3 - var
        4 - op
    """
    for char in expr:
        if char == '(':
            n = n+1
            if (state == 3) | (state == 2):
                print("Bledne wyrazenie 0")
                return False
            state = 1
            continue

        if char == ')':
            n = n-1
            if (n < 0) | (state == 1) | (state == 4):
                print("Bledne wyrazenie 1")
                return False
            state = 2
            continue

        if char == '~':
            if (state == 2) | (state == 3):
                print("Bledne wyrazenie 2")
                return False
            continue

        if char in VARS:
            if (state == 2) | (state == 3):
                print("Bledne wyrazenie 2")
                return False
            state = 3
            if (char != "0") & (char != "1"):
                vars_set.update(char)
            continue

        if char in OPS:
            if (state == 1) | (state == 4):
                print("Bledne wyrazenie 3")
                return False
            state = 4
            continue

    vars_set = sorted(vars_set)

    if (n == 0) & (state != 4) & (expr != ""):
        print("Wyrazenie jest skladniowo poprawne")
        print("Zbior zmiennych:")
        print(vars_set)
        print()
        return vars_set
    else:
        print("Bledne wyrazenie 4")
        return False


def find_minterms(expr, vars_set):
    minterms = []
    for i in range(0, len(vars_set) ** 2):
        tmp = i
        tmp_expr = expr

        for var in reversed(vars_set):
            tmp_expr = tmp_expr.replace(var, str(tmp % 2))
            tmp /= 2
            tmp = int(tmp)

        #print(tmp_expr + "\n")
        if eval(tmp_expr):
            minterms.append(i)
    return minterms


def group_bins(bins):
    grouped_bins = defaultdict(list)
    for number in bins:
        how_many_ones = 0
        for char in number:
            if char == '1':
                how_many_ones += 1
        grouped_bins[how_many_ones].append(number)
    return grouped_bins


def join_bins(grouped_bins): #join bins that differ max at 1 pos recursively

    joined_bins = defaultdict(list)
    used_bins = []
    for group in grouped_bins:
        for bin1 in grouped_bins[group]:

            if group+1 in grouped_bins:
                for bin2 in grouped_bins[group+1]:
                    tmp = ''
                    diff_counter = 0
                    for i in range(0,len(bin1)):
                        if bin1[i] != bin2[i]:
                            tmp += '-'
                            diff_counter += 1
                            if diff_counter > 1:
                                break
                        else:
                            tmp += bin1[i]
                    if diff_counter < 2:
                        joined_bins[group].append(tmp)
                        used_bins.append(bin1)
                        used_bins.append(bin2)

            if bin1 not in used_bins:
                joined_bins[group].append(bin1)

    #print(grouped_bins)
    #print(joined_bins)
    for group in joined_bins:
        joined_bins[group] = list(set(joined_bins[group]))

    if grouped_bins == joined_bins:
        return joined_bins
    else:
        return join_bins(joined_bins)


def solve_cross_table(joined_bins, bins_minterms):
    solution = []
    available_bins = []
    minterms_not_crossed_yet = list(bins_minterms)
    for group in joined_bins:
        for bin in joined_bins[group]:
            available_bins.append(bin)

    for minterm in bins_minterms:
        tmp = None
        for bin in available_bins:
            flag = True
            for i in range(0, len(minterm)):
                if (minterm[i] != bin[i]) & (bin[i] != '-'):
                    flag = False
            if flag:
                if tmp is None:
                    tmp = bin
                else:
                    tmp = -1
                    break
        if (tmp is not None) & (tmp != -1):
            solution.append(tmp)
            minterms_not_crossed_yet.remove(minterm)
            for mint in bins_minterms:
                if mint in minterms_not_crossed_yet:
                    flag = True
                    for i in range(0, len(mint)):
                        if (mint[i] != tmp[i]) & (tmp[i] != '-'):
                            flag = False
                    if flag:
                        minterms_not_crossed_yet.remove(mint)
            available_bins.remove(tmp)

    #Powyzej wykreslanie pojedynczych X, poniżej reszta

    currently_available_bins = list(available_bins)
    for minterm in bins_minterms:
        if minterm in minterms_not_crossed_yet:
            for bin in available_bins:
                if bin in currently_available_bins:
                    flag = True
                    for i in range(0, len(minterm)):
                        if (minterm[i] != bin[i]) & (bin[i] != '-'):
                            flag = False
                    if flag:
                        solution.append(bin)
                        if minterm in minterms_not_crossed_yet:
                            minterms_not_crossed_yet.remove(minterm)
                        for mint in bins_minterms:
                            if mint in minterms_not_crossed_yet:
                                flag = True
                                for i in range(0, len(mint)):
                                    if (mint[i] != bin[i]) & (bin[i] != '-'):
                                        flag = False
                                if flag:
                                    minterms_not_crossed_yet.remove(mint)
                    currently_available_bins.remove(bin)

    #print(available_bins)
    #print(minterms_not_crossed_yet)

    return solution


def convert_bins_to_expression(bin_solution, vars_set):
    expression = ''

    for i in range(0, len(bin_solution)):
        bin_solution[i] = bin_solution[i][2:]

    for bin in bin_solution:
        for i in range(0, len(vars_set)):
            if bin[i] == '1':
                expression += vars_set[i]
            if bin[i] == '0':
                expression += ('~' + vars_set[i])
        expression += ' + '

    expression = expression[0: len(expression)-2]
    print("Uproszczone wyrazenie:")
    return expression


def simplify_expression(vars_set, minterms):
    print("Mintermy:")
    print(minterms)

    bins = [];
    how_many_bits_str = '#0' + str(len(vars_set)+2) + 'b'
    for minterm in minterms:
        bins.append(format(minterm, how_many_bits_str))

    print("Mintermy bin: ")
    print(bins)

    grouped_bins = group_bins(bins)
    print("Pogrupowane po ilości jedynek: ")
    print(grouped_bins)

    joined_bins = join_bins(grouped_bins)
    print("Polaczone: ")
    print(joined_bins)

    bin_solution = solve_cross_table(joined_bins, bins)
    print("Rozwiazanie bin: ")
    print(bin_solution)

    return convert_bins_to_expression(bin_solution, vars_set)


def main(expr):
    print("Wyrażenie do uproszczenia:")
    print(expr)
    if expr == "":
        print("Nie ma czego upraszczać.")
        return
    vars_set = check_if_valid(expr)

    expr = expr.replace('~', ' not ')
    print(expr)

    minterms = find_minterms(expr, vars_set)

    se = simplify_expression(vars_set, minterms)
    if se != '':
        print(se)
    else:
        print(eval(expr))


if __name__ == "__main__":
    main("~0 ^ (a & b)")
    #main("p ^ (w & q)")
    #main("p | (w & q)")
    #main("(p | q) & r")
    #main("p|q & (w | q)")
    #main("p | q | (a & q | p) & a")
    #main("~0 ^ (a & ~b)") #nie dziala bo ewaluowane jest wyrazenie - not 0 ^ (0 &  not 0)
    #main("")