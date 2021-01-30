from flask import Flask
from flask_restful import Resource, Api

from subprocess import check_output
from multiprocessing import Process
import os
import json

app = Flask(__name__)
api = Api(app)

def get_script_output (cmd):
    print("[get_script_output] cmd = {}".format(cmd))
    try:
        return check_output(cmd, shell=True, text=True)
    except:
        return check_output(cmd, shell=True, universal_newlines=True)

def run_cmd():
    return get_script_output(os.environ['API_CMD'])

def run_cmd_async():
    print("[run_cmd_async] output = {}".format(run_cmd()))

def run_cmd_argv():
    body = request.get_json(force=True)
    cmd = "{} {}".format(os.environ['API_CMD'], body['argv'])
    return get_script_output(cmd)

def run_cmd_async_argv():
    print("[run_cmd_async] output = {}".format(run_cmd_argv()))

class AsyncCmdApi(Resource):
    def get(self):
        async_process = Process( 
            target=run_cmd_async,
            daemon=True
        )
        async_process.start()
        return {
            'executed': True,
            'async': True
        }
    def post(self):
        c = check_mandatory_param('argv')
        if is_not_ok(c):
            return c, 400

        async_process = Process( 
            target=run_cmd_async_argv,
            daemon=True
        )
        async_process.start()
        return {
            'executed': True,
            'async': True
        }

class CmdApi(Resource):
    def get(self):
        output = run_cmd()
        return {
            'executed': True,
            'details': output
        }
    def post(self):
        c = check_mandatory_param('argv')
        if is_not_ok(c):
            return c, 400

        output = run_cmd_argv()
        return {
            'executed': True,
            'details': output
        }

class RootEndPoint(Resource):
    def get(self):
        return {
            'alive': True
        }

class ManifestEndPoint(Resource):
    def get(self):
        try:
            with open(os.environ['MANIFEST_FILE_PATH']) as manifest_file:
                manifest = json.load(manifest_file)
                return manifest
        except IOError as err:
            return {"error": err}

health_check_routes = ['/', '/health', '/health/']
cmd_routes = ['/cmd', '/cmd-api', '/cmd/', '/cmd-api/']
async_cmd_routes = ['/cmd/async', '/cmd-api/async', '/cmd/async/', '/cmd-api/async/']
manifest_routes = ['/manifest', '/manifest/']

api.add_resource(RootEndPoint, *health_check_routes)
api.add_resource(CmdApi, *cmd_routes)
api.add_resource(AsyncCmdApi, *async_cmd_routes)
api.add_resource(ManifestEndPoint, *manifest_routes)

if __name__ == '__main__':
    app.run()
