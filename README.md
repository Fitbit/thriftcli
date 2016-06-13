## Usage

From the thrift_cli directory:
    ./bin/run <server_address> <endpoint> <path_to_thrift_file> <path_to_json_file>

For example:
    ./bin/run localhost:9090 MyService.doSomething ../my_project/something.thrift request_body.json

This example assumes that:
    1. ../my_project/something.thrift declares a service called MyService
    2. MyService declares an endpoint called doSomething
    3. request_body.json provides the arguments to doSomething as JSON, in the format <field_name>: <value>

Note: The JSON file is not needed for endpoints that take no arguments, and is ignored.

## Testing

From the thrift_cli directory:
    nosetests

To run specific tests:
    nosetests <path_to_test_file>
    (i.e.) nosetests tests/test_thrift_parser.py


