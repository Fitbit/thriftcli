import json
import sys

from thriftcli import ThriftCLI


def _print_help():
    help_text = '\n'.join([
        'Usage:',
        '  ./run server_address endpoint_name thrift_file_path [-I thrift_dir_path...] [request_body_file_path]',
        '  (i.e.) ./run localhost:12201 Animals.create Animals.thrift request.json'
    ])
    print help_text


def _load_request_body(request_body_path):
    if not request_body_path:
        return {}
    with open(request_body_path, 'r') as request_body_file:
        return json.load(request_body_file)


def _parse_args(argv):
    server_address = argv[1]
    endpoint = argv[2]
    thrift_path = argv[3]
    arg_index = 4
    thrift_dir_paths = []
    while argv[arg_index] == '-I' and len(argv) > arg_index + 1:
        thrift_dir_paths.append(argv[arg_index + 1])
        arg_index += 2
    request_body_path = argv[arg_index] if len(argv) > arg_index else None
    request_body = _load_request_body(request_body_path)
    return server_address, endpoint, thrift_path, thrift_dir_paths, request_body


def main():
    if len(sys.argv) < 4:
        _print_help()
        sys.exit(1)
    server_address, endpoint, thrift_path, thrift_dir_paths, request_body = _parse_args(sys.argv)
    cli = ThriftCLI()
    try:
        cli.setup(thrift_path, server_address, thrift_dir_paths)
        result = cli.run(endpoint, request_body)
        if result is not None:
            print result
    finally:
        cli.cleanup()


if __name__ == '__main__':
    main()
