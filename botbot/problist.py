"""Associating issues with a file"""

class FileProblems:
    def __init__(self, fi, prob):
        self.fi = fi
        self.probs = {prob}

    def add(self, prob):
        """Add a problem to this file"""
        self.probs.add(prob)

class ProblemList:
    """A dictionary of files and their issues"""
    def __init__(self):
        self.problems = dict()

    def probcount(self):
        allp = [p for p in list(self.problems.values())]
        return len(allp)

    def add_problem(self, fi, prob):
        """Associate an issue with a file"""
        if fi.path in self.problems:
            self.problems[fi.path].add(prob)
        else:
            self.problems[fi.path] = FileProblems(fi, prob)

    def files_with_problem(self, prob):
        """Get a list of files with a given problemp"""
        i = iter(self.problems.items())
        return [p[1] for p in i if prob in p[1].probs]

    def files_by_user(self, uid):
        """Get a list of bad files belonging to the given user"""
        i = iter(self.problems.items())
        return [p for p in i if p[1].uid == uid]

    def problem_users(self):
        """
        Kinda mean, but returns a list of users who have bad files, sorted
        by number of bad files.
        """
        i = iter(self.problems.items())
