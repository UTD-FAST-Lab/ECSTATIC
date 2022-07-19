import json

from pydriller import Repository, Git;
import os

from src.ecstatic.runners.AbstractCommandLineToolRunner import AbstractCommandLineToolRunner
from src.ecstatic.toolreverter.Reverter import Reverter, ReverterFactory

# Takes in a list of violations, a github repository and the commits to search between
#
# For Each violation
# spawn a search thread that is composed of, the violation to recreate, the repository to search
# a search will return the hash of the commit, the commit message and the github repository url that the violation was first not recreated in


# rules for search
# cut in half, if recreated, go left, if not go right, repeat until you can no longer go left (with recreating the violation)
# there are some potential edge cases but this is alright for now.

# we have to modify pom.xml of the WalaInterface Project but that is fine (just change version of the wala artifact in the pom.xml)
from src.ecstatic.util.PotentialViolation import PotentialViolation
from src.ecstatic.util.UtilClasses import FuzzingJob
from src.ecstatic.violation_checkers.AbstractViolationChecker import AbstractViolationChecker


class SearchResult:

    def __init__(self, commit, violation):
        self.found_commit = commit;
        self.violation=violation.as_dict();

    def __str__(self):
        return json.dumps({'fix_commit':self.found_commit,'violation':self.violation});


class BinarySearch():

    def __init__(self, gitrepo: str, from_tag, to_tag, violations: [PotentialViolation], toolrunner:AbstractCommandLineToolRunner, revert_tool: Reverter, checker: AbstractViolationChecker):
        self.gitrepo = gitrepo;
        self.from_tag = from_tag;
        self.to_tag = to_tag;
        self.violations = violations;
        self.ROOT_SEARCH_DIRECTORY = "/binary_search_project";
        self.toolrunner = toolrunner;
        self.revert_tool = revert_tool;
        self.checker = checker;

        # spawn different searches and handle git repo and such

    def performsearch(self) -> [SearchResult]:
        results = []
        #TODO::This needs to be based on the tool, for now we will just get Wala
        if not os.path.exists("/bsearch_results"):
            os.mkdir("/bsearch_results")
        failedbuilds = []
        for violation in self.violations:
            if(not violation.violated):
                continue;
            repo = self.setup_repo(str(self.gitrepo), self.from_tag, self.to_tag);
            git_repo =  Git(str(self.gitrepo));
            all_commits = []
            for x in repo.traverse_commits():
                if x.committer_date.date() < git_repo.get_commit_from_tag(self.from_tag).committer_date.date():
                    continue;
                if x.hash in failedbuilds:
                    continue;
                all_commits.append(x);
            all_commits.sort(key=lambda x: x.committer_date.date());

            left =0;
            right= len(all_commits);
            while left < right:
                inx = (int)((left+right)/2)
                commit = all_commits[inx];
                if not self.revert_tool.revert_tool(repo,commit.hash):
                    # remove build and restart search cause I think this is easier then doing anything else
                    failedbuilds.append(commit.hash);
                    all_commits.remove(commit)
                    right=right-1;
                    continue;
                job1: FuzzingJob = violation.job1.job;
                job2: FuzzingJob = violation.job2.job;

                fjob1 = self.toolrunner.run_job(job1,"/bsearch_results",entrypoint_s=True)
                fjob2 = self.toolrunner.run_job(job2,"/bsearch_results",entrypoint_s=True)
                if fjob1 is None or fjob2 is None:
                    failedbuilds.append(commit.hash);
                    all_commits.remove(commit);
                    right=right-1;
                    continue;

                new_violation = self.checker.check_for_violation(t=(fjob1,fjob2,job1.option_under_investigation));
                if len(*new_violation)==0:
                    right=inx;
                else:
                    found= False;
                    for x in new_violation:
                        if x.othereq(violation):
                            found=True;

                    if found:
                        #this commit recreated the violation
                        left=inx+1;
                    else:
                        #this commit did not recreate the violation
                        right=inx;
            results.append(SearchResult(all_commits[right],violation));
        return results;


    def setup_repo(self, gitrepo, from_tag, to_tag):
        path = self.initiate_repo(gitrepo);
        git_repo = Repository(path_to_repo=path, from_tag=from_tag, to_tag=to_tag);
        return git_repo;

    # method that clones repo and make its local if not already exist
    def initiate_repo(self, gitrepo):
        return '/binary_search_project/WALA'

