import socket
import select
import argparse
from flask import Flask, url_for

from flask import request
from flask import Response
from flask import json
from flask import jsonify
import os
from git import Repo
import time
import pandas as pd

app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_work():
    """ worker request work items here.
    response: { 'commit_number': commit_number,
                'status': status }
    """

    status = 'ok'
    if not cc_manager.is_ready:
        status = 'not ready'
        commit_number = ''
    elif len(cc_manager.commits) == 0:
        status = 'done'
        commit_number = ''

        if not cc_manager.is_finished and cc_manager.have_commits_returned('all'):
            cc_manager.is_finished = True

            print("All commits have been sent. Finishing up...")

            # # wait for all returns
            # returned = False
            # while not returned:
            #     returned = cc_manager.have_commits_returned('all')
            #     time.sleep(1)
            #     print("Waiting for returns..")

            cc_manager.finalise()

    else:
        commit = cc_manager.commits.pop(0)
        commit_number = commit.hexsha

        if cc_manager.commit_status[commit_number] != 'ready':
            raise Exception("This Commitnumber {0} has already been processed".format(commit_number))
        cc_manager.commit_status[commit_number] = 'sent'

        print("new length of commit_numbers = ", len(cc_manager.commits))

    data = {
        'commit_number': commit_number,
        'status': status
    }

    resp = jsonify(data)
    resp.status_code = 200


    cc_manager.add_time(commit_number, time.clock())
    return resp


@app.route('/', methods=['POST'])
def post_result():

    t_end = time.clock()
    data = request.json

    # print("worker id: ", data['worker_id'])
    # print("worker cc: ", data['cc'])
    commit_number = data['commit_number']

    # add cc result to manager
    cc_manager.add_cc_t_end(data['commit_number'], int(data['cc']), t_end, data['worker_id'])

    # update commmit_status
    if cc_manager.commit_status[commit_number] != 'sent':
        raise Exception("This Commitnumber {0} has not been sent or already finished".format(commit_number))
    cc_manager.commit_status[commit_number] = 'finished'

    return "JSON Message: " + json.dumps(request.json)


@app.route('/', methods=['PUT'])
def put_ready():
    """ pass any message to PUT method to set server to ready for processing workers"""

    print("Master Server is Ready")
    cc_manager.start_time = time.clock()
    cc_manager.is_ready = True

    resp = jsonify({'status': 'Ready'})
    resp.status_code = 200
    return resp

class CodeComplexityMaster:

    def __init__(self, repo=''):

        print("Initialising Master...")

        # GIT repository settings
        self.git_repository = repo
        self.root_repo_dir = "./repo"
        self.commits = []
        # {commit: 'ready'/'sent'/'finished'}
        self.commit_status = {}

        self.cc_per_commit = {}
        self.repo = None

        # ready to process workers
        self.is_ready = False
        self.is_finished = False

        self.start_time = None

        # {commit_number: [t1, t2, t2-t1]}
        self.time_table = {}

    def setup_gitrepo(self):
        """ setup git repository """

        repo_dir = self.root_repo_dir
        if not os.path.exists(repo_dir):
            os.makedirs(repo_dir)

        if not os.listdir(repo_dir):
            print('cloning repository into directory: {0}'.format(repo_dir))
            Repo.clone_from(self.git_repository, repo_dir)
            print('cloning finished')

        self.repo = Repo(repo_dir)
        assert not self.repo.bare

        self.commits = list(self.repo.iter_commits('master'))
        self.commit_status = {c.hexsha: 'ready' for c in self.commits}
        # self.cc_per_commit = {commit: None for commit in self.commits}
        self.cc_per_commit = {}

        print("Repository setup complete")

    def have_commits_returned(self, number='all'):
        """ return True if all commits have returned and are in state finished"""

        if number == 'all':
            for commit_number, status in self.commit_status.items():
                if status != 'finished':
                    print("Commit {0} is not finished, current status {1}".format(commit_number, status))
                    return False

            return True


    def finalise(self):

        # check if all commits have returned
        if not self.have_commits_returned('all'):
            raise Exception("Not all commits have returned finished. Can't finalise")

        # calculate time differences
        for commit_number in self.time_table:
            self.time_table[commit_number].append(self.time_table[commit_number][1] - self.time_table[commit_number][0])

        total_cc = sum([x[0] for x in self.cc_per_commit.values()])
        total_time = sum([l[2] for l in self.time_table.values()])

        print("COMPLETE, total CC = ", total_cc)
        print("COMPLETE, total time = ", total_time)

        final = [(self.cc_per_commit[c][1], c, self.time_table[c][0], self.time_table[c][1], self.time_table[c][2], int(self.cc_per_commit[c][0])) for c in self.commit_status]
        df = pd.DataFrame(final, columns=['WorkerID', 'CommitNumber', 'T0', 'T1', 'deltaT', 'Complexity'])

        nClients = len(set([x[0] for x in final]))
        # save to file
        df.to_csv('run_nclients_{0}.csv'.format(nClients))

        summary_df = [(nClients, total_time, total_cc)]
        df_summary = pd.DataFrame(summary_df, columns=['nClients', 'total_time', 'total_cc'])
        # save to file
        df_summary.to_csv('run_summary_nclients_{0}.csv'.format(nClients))


    def add_cc_t_end(self, commit_number, cc, t_end, worker_id):

        cc_manager.cc_per_commit[commit_number] = [cc, worker_id]

        if commit_number not in self.time_table:
            raise Exception("cant have end time without start time")

        self.time_table[commit_number][1] = t_end


    def add_time(self, commit_number, t):
        self.time_table[commit_number] = [t, 0]



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='host ip of server.'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='port of server.'
    )

    FLAGS, unparsed = parser.parse_known_args()

    # get gitrepo from config file
    git_repo = None
    with open('cyclo_config.json') as f:
        config_json = json.loads(f.read())
        git_repo = config_json['git_repo']

    # global cc_manager
    cc_manager = CodeComplexityMaster(repo=git_repo)
    cc_manager.setup_gitrepo()

    # run application with set flags
    app.run(host=FLAGS.host, port=FLAGS.port)
