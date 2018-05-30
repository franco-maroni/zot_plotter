import argparse
import json

import itertools

import os
#import matplotlib
from parse_output import VerificationResult, VerificationTrace, ZotTrace, ZotResult
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from __builtin__ import staticmethod
import utils
import sys
import pkg_resources

import config as cfg

SHIFT = 5

def get_plot_styles_list(settings, greyscale=False):
    # ONELINE  return [''.join(t) for t in list(itertools.product(
    # settings["markers"], setting["line_styles"],setting["colors"]))]
    markers = settings["markers"]
    line_styles = settings["line_styles"]
    colors = ["k"] if greyscale else settings["colors"]
    tuples_list = list(itertools.product(markers, line_styles, colors))
    strings_list = [''.join(t) for t in tuples_list]
    # print strings_list
    return strings_list


def plot_vars_from_records(steps, records, bool_set, settings, boolean_base):
    step_list = range(steps + 1)
    styles_list = get_plot_styles_list(settings, cfg.PLOT_CFG["greyscale"])
    excluded_vars = settings['exclude_vars']
    counters_list = [k for k in records.keys() if k not in excluded_vars + list(bool_set)]
    # couple list of counters to plot with list of styles
    var_styles_dict = dict(zip(counters_list, styles_list))
    print(var_styles_dict)
    for var_id in counters_list:  # plot counters
        var_style = var_styles_dict.get(var_id, '+:k')
        var_lw = 2
        var_msize = 5
        print 'Plotting: {}:\n {}'.format(var_id, records[var_id])
        plt.plot(step_list, [float(x) for x in records[var_id]], var_style, label=var_id,
                 linewidth=var_lw, markersize=var_msize)
    for var_id in bool_set:  # plot boolean vars
        prefix = var_id.split('_')[0]
        var_settings = settings['boolean_vars'][prefix] if prefix in settings['boolean_vars'] else {}
        marker = var_settings['marker'] if 'marker' in var_settings else 'o'
        s = var_settings['s'] if 's' in var_settings else 10
        shift = var_settings['shift'] if 'shift' in var_settings else 0
        # if boolean var is true,
        bool_series = \
            [boolean_base + int(var_id.split('_')[1]) + shift if j
                in records[var_id] else boolean_base for j in range(steps + 1)]
        print("plotting {}: {}".format(var_id, bool_series))
        plt.scatter(step_list, bool_series, label=var_id,
                    s=s, marker=marker, alpha=0.5)


class VerificationTask:
    resource_package = __name__  # Could be any module/package name
    file_dir = pkg_resources.resource_filename(resource_package, "")

    # base directory
#    file_dir = os.path.dirname(os.path.realpath(__file__))
    base_dir = os.environ.get('VERIF_DIR',
                              file_dir)
    # standard result file for zot (containing verification outcome)
    result_file = 'output.1.txt'
    # standard history file for zot (containing output trace)
    hist_file = 'output.hist.txt'

    def __init__(self,
                 plotonly_folder,
                 display=False,
                 graphical_conf_path='plot_cfg.json'):
        '''
        Constructor
        '''
        self.verification_result = VerificationResult()
        self.output_trace = VerificationTrace()
        self.display = display
        self.graphical_conf_path = os.path.abspath(graphical_conf_path)
        self.figure_path = None
        self.result_dir = self.app_dir = os.path.abspath(plotonly_folder)
        print(self.app_dir)
        self.app_name = self.app_dir.split(os.path.sep)[-1]
        self.process_zot_results(self.result_dir,
                                 os.path.join(self.result_dir,
                                              self.hist_file))

    def parse_zot_trace(self, file_path=None):
        """Create new ZotTrace object after parsing history file."""
        print 'parse_zot_trace({})'.format(file_path)
        if not file_path:
            file_path = os.path.join(self.result_dir, self.hist_file)
        self.output_trace = ZotTrace(file_path)

    def process_zot_results(self, result_dir=None, trace_file=None):
        '''
        get results from file and, if SAT, parse and plot the trace
        '''
        if not result_dir:
            result_dir = self.result_dir
        if not trace_file:
            trace_file = self.hist_file
        print 'process_zot_result({},{})'.format(result_dir, trace_file)
        self.verification_result = ZotResult(result_dir)
        if self.verification_result.outcome == 'sat':
            self.parse_zot_trace(os.path.join(result_dir, trace_file))

    def plot_trace(self):
        """Plot the trace provided in the records dictionary."""
        print "Opening {}".format(self.graphical_conf_path)
        with open(self.graphical_conf_path) as settings_file:
            settings = json.load(settings_file)
        file_name = self.app_name if self.app_name is not None else "plot"
        steplist = range(self.output_trace.time_bound + 1)
        #  first round to get the maximum y value
        my_dpi = 96
        plt.figure(figsize=(1460/my_dpi, 900/my_dpi), dpi=my_dpi)
        y_max_boolean = max([float(var_id.split('_')[1]) for var_id in self.output_trace.bool_set])
        y_max_counters = max([max([float(y) for y in self.output_trace.records[var]])
                              for var in self.output_trace.records.keys()
                              if var not in settings['exclude_vars'] + list(self.output_trace.bool_set)])

        y_max = y_max_counters + y_max_boolean + 2 * SHIFT
        boolean_base = y_max_counters + SHIFT
        print('y_max: {}'.format(y_max))
        # plot variables' values

        plt.subplot(111)
        plot_vars_from_records(self.output_trace.time_bound,
                               self.output_trace.records,
                               self.output_trace.bool_set,
                               settings,
                               boolean_base)
        plt.ylim([0, y_max + 1])
        rounded_totaltime = \
            map(lambda t: round(float(t.strip('?')), 2),
                self.output_trace.records['now'])
        plt.ylabel(cfg.PLOT_CFG["y-label"]["text"], fontsize=cfg.PLOT_CFG["y-label"]["fontsize"])
        plt.xticks(steplist, rounded_totaltime, rotation=45)
        plt.xlabel(cfg.PLOT_CFG["x-label"]["text"], fontsize=cfg.PLOT_CFG["x-label"]["fontsize"])
        fontP = FontProperties()
        fontP.set_size(cfg.PLOT_CFG["legend"]["size"])
        plt.legend(prop=fontP, loc='upper left')
#        plt.legend(loc='upper left')
        plt.grid()
        # highlight in red the looping suffix of the output trace
        if 'LOOP' in self.output_trace.records:
            plt.axvspan(self.output_trace.records['LOOP'],
                        self.output_trace.time_bound,
                        color=cfg.PLOT_CFG["highlighted-area"]["color"],
                        alpha=cfg.PLOT_CFG["highlighted-area"]["alpha"])
        plt.axhline(y=boolean_base)
        plt.axhspan(ymin=boolean_base,
                    ymax=y_max,
                    color=cfg.PLOT_CFG["boolean-area"]["color"],
                    alpha=cfg.PLOT_CFG["boolean-area"]["alpha"])

    #    plt.tight_layout()
        time_str = self.verification_result.timestamp_str
        utils.make_sure_path_exists(os.path.join(self.result_dir, "imgs"))
        self.figure_path = os.path.join(self.result_dir, "imgs",
                                        "{}_{}.png".format(file_name,
                                                           time_str))
        print "saving figure in {}".format(self.figure_path)
        plt.savefig(self.figure_path,
                    facecolor='w', edgecolor='k')
        if self.display:
            plt.show()
        return os.path.abspath(self.figure_path)

    def __str__(self):
        return '''Spark Verification Task:
                result_dir: {} \n
                app_name: {} \n
                app_dir: {} \n
                verification_result {} \n
                output_trace: {} \n
                display: {}
                '''.format(self.result_dir,
                           self.app_name,
                           self.app_dir,
                           self.verification_result,
                           self.output_trace,
                           self.display)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=
        """
        Zot Plotter CLI
        """
    )
    parser.add_argument('dir', help='directory containing the results  of a zot verification task')
    parser.add_argument('-d', '--display', dest='display', action='store_true',
                              help='display the results on a popup window')
    args = parser.parse_args()
    t = VerificationTask(args.dir, args.display)
    t.plot_trace()
