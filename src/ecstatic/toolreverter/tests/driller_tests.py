from pydriller import Repository
from pydriller import Git
import xml.etree.ElementTree as ET

#Tags we want to traverse between
from_tag = 'v1.5.5'
to_tag = 'v1.5.7'
filepath_to_pom = "C:\wala_revert_test\WALA\pom.xml";
wala_git = Git('/wala_revert_test/WALA');
wala_repo = Repository("/wala_revert_test/WALA",
                       from_commit=wala_git.get_commit_from_tag('v1.5.5').hash,
                       to_commit=wala_git.get_commit_from_tag('v1.5.7').hash,
                       order='date-order');

command_run = "gradle clean publishToMavenLocal -x test -x javadoc -x testClasses -x testFixturesJavadoc"

print(wala_git.get_commit_from_tag('v1.5.5').hash);
ET.register_namespace('',"http://maven.apache.org/POM/4.0.0")

count  = 0;
for commit in wala_repo.traverse_commits():
    if commit.committer_date < wala_git.get_commit_from_tag('v1.5.5').committer_date:
        continue;
    if commit.committer_date > wala_git.get_commit_from_tag('v1.5.7').committer_date:
        continue;
    wala_git.checkout(commit.hash);
    pom_tree = ET.parse(filepath_to_pom);
    root = pom_tree.getroot();
    print(root[3].text);
    count+=1;
print(count);
