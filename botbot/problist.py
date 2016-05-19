"""Associating issues with a file"""

class ProblemList:
    """A dictionary of files and their issues"""
    def __init__(self):
        self.problems = dict()

    def add_problem(self, path, prob):
        """Associate an issue with a file"""
        if path in self.problems:
            self.problems[path].add(prob)
        else:
            self.problems[path] = {prob}

    def file_list(self, prob):
        """Get a list of files with a given problem"""
        i = iter(self.problems.items())
        return [p[0] for p in i if prob in p[1]]
