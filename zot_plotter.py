from plot_output import VerificationTask
import argparse

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