import re
import sys
import csv

interval_regx = re.compile("(\025\d+_\d+)")

orig_cex_intervals = []
annot_cex_intervals = []

adjusted_timestamps = []    # timestamps that were rewritten because if silences/subregions


def parse_orig_cex(path):
    with open(path, "rU") as file:
        for index, line in enumerate(file):
            interv_reg_result = interval_regx.findall(line)
            if interv_reg_result:
                if len(interv_reg_result) > 1:
                    print "More than one interval on a line:  line# " + str(index)
                    return
                for interval_str in interv_reg_result:
                    interval = [None, None]
                    interval_split = interval_str.replace("\025", "").split("_")
                    interval[0] = int(interval_split[0])
                    interval[1] = int(interval_split[1])
                    orig_cex_intervals.append(interval)
            else:
                continue


def parse_annot_cex(path):
    with open(path, "rU") as file:
        for index, line in enumerate(file):

            if line.startswith("%com:") and\
                ("silence" in line) or ("subregion" in line):

                adjusted_timestamps.append(annot_cex_intervals[-1])
                print annot_cex_intervals[-1]

            interv_reg_result = interval_regx.findall(line)
            if interv_reg_result:
                if len(interv_reg_result) > 1:
                    print "More than one interval on a line:  line# " + str(index)
                    return
                for interval_str in interv_reg_result:
                    interval = [None, None]
                    interval_split = interval_str.replace("\025", "").split("_")
                    interval[0] = int(interval_split[0])
                    interval[1] = int(interval_split[1])
                    annot_cex_intervals.append(interval)
            else:
                continue

def compare_intervals(orig_cex_intervals, annot_cex_intervals):
    problems = []
    off_by_one_count = 0

    for index, interval in enumerate(orig_cex_intervals):

        plus_plus = [interval[0]+1, interval[1]+1]
        plus_same = [interval[0]+1, interval[1]]
        same_plus = [interval[0], interval[1]+1]

        minus_minus = [interval[0]-1, interval[1]-1]
        minus_same = [interval[0]-1, interval[1]]
        same_minus = [interval[0], interval[1]-1]

        off_by_ones = (plus_plus, plus_same, same_plus,
                       minus_minus, minus_same, same_minus)


        if interval not in annot_cex_intervals:
            off_by_one = False
            adjusted_by_comment = False

            # check for off by one
            for interv in off_by_ones:
                if interv in annot_cex_intervals:
                    print "found off by one: " + str(interv)
                    off_by_one = True
                    off_by_one_count += 1

            # check for rewritten timestamp because of silence/subregion comment
            if interval[0] in [intrv[0] for intrv in adjusted_timestamps]:
                adjusted_by_comment = True

            if not (off_by_one or adjusted_by_comment):
                problems.append(interval)
                #print "found a problem: " + str(interval)
    print "\n\n# of off by ones: " + str(off_by_one_count)
    print "# of otherwise inconsistent intervals: " + str(len(problems))
    print "\nproblem intervals: " + str(problems)


def print_usage():
    print "USAGE: "
    print "python clan_intervals.py orig_cex_file annotated_cex_file"

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print_usage()

    orig_cex_file = sys.argv[1]
    annot_cex_file = sys.argv[2]

    parse_orig_cex(orig_cex_file)
    parse_annot_cex(annot_cex_file)

    compare_intervals(orig_cex_intervals, annot_cex_intervals)
