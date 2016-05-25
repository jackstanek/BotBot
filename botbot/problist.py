"""Associating issues with a file"""

class FileProblems:
    def __init__(self, fi, prob):
        self.fileinfo = fi
        self.probs = {prob}

    def add(self, prob):
        """Add a problem to this file"""
        self.probs.add(prob)

class ProblemList:
    """A dictionary of files and their issues"""
    def __init__(self):
        self.problems = dict()

    def probcount(self):
        """Get the total number of problems"""
        allp = [p for p in list(self.problems.values())]
        return len(allp)

    def current_problems(self):
        """Get a list of problems that files in the list have"""
        pl = [p.probs for p in self.problems.values()]
        if len(pl) > 0:
            return set.union(*pl)
        else:
            return {}

    def add_problem(self, fi, prob):
        """Associate an issue with a file"""
        if fi.path in self.problems:
            self.problems[fi.path].add(prob)
        else:
            self.problems[fi.path] = FileProblems(fi, prob)

    def files_by_problem(self):
        """
        Get a dictionary where keys are problem names and values are a set
        of FileInfo objects with that problem
        """
        fbp = dict()
        for prob in self.current_problems():
            fbp[prob] = set(p.fileinfo for p in self.problems.values() if prob in p.probs)

        return fbp

    def files_by_user(self, uid):
        """Get a list of bad files belonging to the given user"""
        i = self.problems.items()
        return [p for p in i if p[1].uid == uid]

    def problem_users(self):
        """
        Kinda mean, but returns a list of users who have bad files, sorted
        by number of bad files.
        TODO: Implement this
        """
        pass
