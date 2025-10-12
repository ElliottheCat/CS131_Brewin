from brewparse import parse_program



program_source="""
def main() {
    var x;
}
"""


def main():
    ast=parse_program(program_source,True)
    # added save to png in plot.py, doesn't affect other stuff. 


if __name__ == '__main__':
    main()