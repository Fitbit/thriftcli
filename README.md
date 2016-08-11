## About

ThriftCLI is a CLI tool for executing RPC's via the Thrift protocol.

## Installation

First, navigate to the project directory (contains setup.py):

Next, install the CLI tool and thrift:
```
python setup.py install
brew install thrift
```

Now you have a command line application called "thriftcli" in your path:
```
thriftcli server_address endpoint_name thrift_file_path [options]
```

Arguments:
- **server_address**       URL to send the request to. This server should listen for and implement the requested endpoint.
- **endpoint_name**        Service name and function name representing the request to send to the server.
- **thrift_file_path**     Path to the thrift file containing the endpoint\'s declaration.

Options:
- **-h --help**            Display a help message
- **-I --includes [thrift_dir_path...]**
                           Path to additional directory to search in when locating thrift file dependencies.
- **-b --body [request_body]**
                           The request body to send with the endpoint.
                           Must be in one of the following formats:
                            JSON body, such as '{"request": {"person": {name": "joe", "id": 2}}}'.
                            Java Thrift body, such as 'request:MyRequest(person:Person(name:joe, id:2))'.
                            Path to a file containing any of the above formats.
- **-z --zookeeper**       Treat the server address as a Zookeeper instance, and make the request to the service being provided at the given path.
- **-c --cleanup**         Delete generated code from filesystem after execution
- **-j --json**            Print result in JSON format

## Examples

```
thriftcli localhost:9090 Calculator.ping ./Calculator.thrift
thriftcli localhost:9090 Calculator.add ./Calculator.thrift --body add_request_body.json
thriftcli localhost:9090 Calculator.doWork ./Calculator.thrift --body '{"work": {"num1": 1, "num2": 3, "op": "ADD"}}'
thriftcli localhost:9090 Calculator.doWork ./Calculator.thrift --body 'Work(num1:1,num2:3,op:ADD)'
thriftcli localhost:12201 Animals.get ~/Animals.thrift -I ~/thrifts/ --body ~/animals_get.json
thriftcli localhost:2181/animals -z Animals.get ~/Animals.thrift --body ~/animals_get.json
```

These examples assume that:

- './Calculator.thrift' declares a service called 'Calculator'
- 'Calculator' declares functions called 'ping', 'add', and 'doWork'
- The 'Calculator.ping' endpoint takes no arguments
- The 'Calculator.add' endpoint takes arguments that agree with the contents of 'add_request_body.json'
- The 'Calculator.doWork' endpoint has an argument labeled 'work' that is a struct consisting of fields 'num1', 'num2', and 'op'
- The 'Calculator' service is being run at localhost:9090
- '~/Animals.thrift' includes thrift files found in '~/thrifts/'
- '~/Animals.thrift' declares a service called 'Animals'
- 'Animals' declares a function called 'get'
- The 'Animals.get' endpoint takes arguments that agree with the contents of '~/animals_get.json'
- The 'Animals' service is being provided by localhost:12201
- localhost:2181 is a running Zookeeper instance providing the 'Animals' service on the '/animals' path

## Limitations

# Conflicting Method Names

Consider two services, A and B, which are both defined in MyThrift.thrift and declare a method named helloWorld.

Assume you're running a server that implements A.helloWorld.

When using ThriftCLI, both endpoints A.helloWorld and B.helloWorld will execute the running server's implementation of A.helloWorld.

This is due to the nature of Thrift and cannot be checked for prior to execution. The ThriftCLI user is responsible for assuring that the correct helloWorld implementation is called.

# Reserved Words

Use of Python reserved words in service definitions is not supported by ThriftCLI.

If you provide ThriftCLI with a thrift file that uses a Python reserved word, or has a dependency that does, running ThriftCLI will fail.

## Contributing

If you would like to contribute to the ThriftCLI project, please use this workflow:
    1. Clone the repository
    2. Create a branch named after your functionality
    3. Implement your changes
       NOTE: If it's your first time contributing to ThriftCLI, include
             a change that adds your name to the CONTRIBUTORS file
    4. Push the branch to the remote repository
    5. File a pull request for your branch and include a description

## Running from Source

If you'd like to run ThriftCLI from its source, without running the install script, navigate to the project directory and run:
```
python -m thriftcli
```

## Testing

From the project directory:

```
nosetests
```
