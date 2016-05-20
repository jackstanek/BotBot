"""Associating issues with a file"""

class FileProblems:
    def __init__(self, uid, prob):
        self.uid = uid
        self.probs = {prob}

    def add(self, prob):
        """Add a problem to this file"""
        self.probs.add(prob)

class ProblemList:
    """A dictionary of files and their issues"""
    def __init__(self):
        self.problems = dict()

    def add_problem(self, fi, prob):
        """Associate an issue with a file"""
        if fi.path in self.problems:
            self.problems[fi.path].add(fi.uid, prob)
        else:
            self.problems[fi.path] = FileProblems(fi.uid, prob)

    def files_with_problem(self, prob):
        """Get a list of files with a given problemp"""
        i = iter(self.problems.items())
        return [p[0] for p in i if prob in p.probs]

    def files_by_user(self, uid):
        """Get a list of bad files belonging to the given user"""
        return 
