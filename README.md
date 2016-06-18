## Usage

First, navigate to the project directory (contains setup.py): 

Next, install the thriftcli Python module and thrift:
```
pip install thrift
python setup.py install
brew install thrift
```

Now you have a command line application called thriftcli in your path:

```
thriftcli server_address endpoint_name thrift_file_path [json_request_body]
```

Arguments:
- **server_address**       URL to send the request to. This server should listen for and implement the requested endpoint.
- **endpoint_name**        Service name and function name representing the request to send to the server.
- **thrift_file_path**     Path to the thrift file containing the endpoint\'s declaration.
- **json_request_body**    Either a JSON string containing the request body to send for the endpoint or a path to such a JSON file.
                           For each argument, the JSON should map the argument name to its value.
                           For a struct argument, its value should be a JSON object of field names to values.
                           This parameter can be omitted for endpoints that take no arguments.

For example:

```
thriftcli localhost:9090 Calculator.ping ./Calculator.thrift
thriftcli localhost:9090 Calculator.add ./Calculator.thrift add_request_body.json
thriftcli localhost:9090 Calculator.doWork ./Calculator.thrift {\\"work\\": {\\"num1\\": 1, \\"num2\\": 3, \\"op\\": \\"ADD\\"}}
```

These example assumes that:

- './Calculator.thrift' declares a service called 'Calculator'
- 'Calculator' declares functions called 'ping', 'add', and 'doWork'
- The 'ping' function takes no arguments
- The 'add' function takes arguments that agree with the contents of 'add_request_body.json'
- The 'doWork' function has an argument labeled 'work' that is a struct consisting of fields 'num1', 'num2', and 'op'

## Testing

From the thriftcli directory:

```
nosetests
```

To run specific tests:

```
nosetests <path_to_test_file>
```

For example:

```
nosetests tests/test_thrift_parser.py
```
