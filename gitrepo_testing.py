##
## Testing Code Complexity and Repo stuff
##
##



from git import Repo
import os
from radon.complexity import cc_rank, cc_visit
import shutil
from itertools import count


ROOT_REPO_DIR = './repo'
repo_counter = count()
repo_dir = ROOT_REPO_DIR + str(next(repo_counter))

if not os.path.exists(repo_dir):
    os.makedirs(repo_dir)

if not os.listdir(repo_dir):
    print('cloning repository into directory: {0}'.format(repo_dir))
    Repo.clone_from("https://github.com/DLTK/DLTK", repo_dir)
    print('cloning finished')

repo = Repo(repo_dir)
assert not repo.bare



heads = repo.heads
master = heads.master
tags = repo.tags
print("heads = {0}, \nmaster = {1} \ntags = {2}".format(heads, master, tags))
print("tag0.tag = {0}".format(tags[0].tag))
print("tag0.commit = {0}".format(tags[0].commit))


fifty_first_commits = list(repo.iter_commits('master', max_count=50))
all_commits = list(repo.iter_commits('master'))
print("First fifty commits = {0}".format(fifty_first_commits))
print("All commits = {0}".format(all_commits))
print("LEN of All commits = {0}".format(len(all_commits)))

first_commit = all_commits[-1]
print("first ever commit = ", first_commit.hexsha)
# repo.commit(first_commit.hexsha)

print("current hexsha = ", repo.head.object.hexsha)

git = repo.git
# git.checkout(all_commits[-1].hexsha)
git.checkout(all_commits[0].hexsha)


################## get all files from repo ####################

from os import walk

files = []
for (dirpath, dirnames, filenames) in walk('./repo0'):
    for filename in filenames:
        if '.py' in filename:
            dirpath = dirpath.replace("\\", "/")
            print(dirpath + '/' + filename)
            files.append(dirpath + '/' + filename)

# print("Files = ", f)

################## calculate cyclomatic complexity ####################


from radon.visitors import ComplexityVisitor
import radon


with open(files[10]) as f:
    data = f.read()
    print(data)

    dat2 = '''
def factorial(n):
    if n < 2: return 1
    return n * factorial(n - 1)

def foo(bar):
    return sum(i for i in range(bar ** 2) if bar % i)
    '''

    # v = ComplexityVisitor.from_code(data)
    # print("Complexity = ", v.)
    cc = radon.complexity.cc_visit(data)
    for cc_item in cc:
        print("complexity = ", cc_item.complexity)