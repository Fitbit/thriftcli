import json
import sys

from thrift_cli import ThriftCLI


def _print_help():
    help_text = '\n'.join([
        'Usage:',
        '  ./run <server_address> <endpoint_name> <thrift_file_path> <json_request_body_file_path>',
        '  (i.e.) ./run localhost:12201 Animals.create Animals.thrift request.json'
    ])
    print help_text


def _load_request_body(request_body_path):
    if not request_body_path:
        return {}
    with open(request_body_path, 'r') as request_body_file:
        return json.load(request_body_file)


def main():
    if len(sys.argv) < 4:
        _print_help()
        sys.exit(1)
    server_address = sys.argv[1]
    endpoint = sys.argv[2]
    thrift_path = sys.argv[3]
    request_body_path = sys.argv[4] if len(sys.argv) > 4 else None
    request_body = _load_request_body(request_body_path)
    cli = ThriftCLI()
    try:
        cli.setup(thrift_path, server_address)
        cli.run(endpoint, request_body)
    finally:
        cli.cleanup()


if __name__ == '__main__':
    main()
