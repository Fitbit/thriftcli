import sys
import getopt
import json
from thrift_cli import ThriftCLI

def print_help():
	help_text = '\n'.join([
		'Usage:',
		'  ./run <server_address> <endpoint_name> <thrift_file_path> <json_request_body_file_path>',
		'  (i.e.) ./run localhost:12201 Animals.create Animals.thrift request.json'
	])
	print help_text

def main():
	server_address = sys.argv[1]
	endpoint = sys.argv[2]
	thrift_path = sys.argv[3]
	request_body_path = sys.argv[4] if len(sys.argv) > 4 else None
	with open(request_body_path, 'r') as request_body_file:
		request_body = json.load(request_body_file)
	cli = ThriftCLI()
	cli.setup(thrift_path, server_address)
	cli.run(endpoint, request_body)

if __name__ == '__main__':
	main()