[![Build Status](https://travis-ci.org/Fitbit/thriftcli.svg?branch=master)](https://travis-ci.org/Fitbit/thriftcli)
[![Coverage Status](https://coveralls.io/repos/github/Fitbit/thriftcli/badge.svg?branch=master)](https://coveralls.io/github/Fitbit/thriftcli?branch=master)

## About

ThriftCLI is a CLI tool for executing RPC's via the Thrift protocol.

## Installation

The easiest way is to use pip:

```
pip install thriftcli
```

Another option is to manually build and compile. First, install the thrift compiler from homebrew: (this only needs to be done once)
```
brew install thrift
```

Then you can build and install it to */usr/local/bin/thriftcli*
```
python setup.py install
```

and you can run it like this: (assuming /usr/local/bin is on your PATH)
```
thriftcli server_address endpoint_name thrift_file_path [options]
```

Alternatively, you can build and start it all at once without installing: (convenient for dev)
```
python -m thriftcli server_address endpoint_name thrift_file_path [options]
```

A last option, if you don't care about wasting a lot of disk space for Docker, is to run from docker:

```
docker run docker.pkg.github.com/fitbit/thriftcli/thriftcli:<VERSION>
```

Available docker images are at https://github.com/Fitbit/thriftcli/packages/

## Running

When first running it can be helpful to do:
```
thriftcli --help
```

This will list all the arguments accepted by the tool. The most common are:
- **server_address**       URL to send the request to. This server should listen for and implement the requested endpoint.
- **endpoint_name**        Service name and function name representing the request to send to the server.
- **thrift_file_path**     Path to the thrift file containing the endpoint\'s declaration.

And the main options:
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
- **-p --proxy [PROXY]**    Access the service via a proxy (for auth reasons) "proxy host:proxy port"
- **-c --cleanup**         Delete generated code from filesystem after execution
- **-j --json**            Print result in JSON format
- **-t --tls**             Use TLS socket if provided
- **-k --tls_key_path**    path to tls key file. Provides client identity to enable mTLS communication.  Has effect only if --tls key is provided
- **-m --cert_verification_mode** Peer certificate validation mode.
                            **none** : server's certificate will not be validated. Connection will be established even if certificate is absent
                            **optional** : server's certificate will be validated if provided. Absence of certificate doesn't prevent the connection
                            **required** : Valid certificate must be provided by the server. This is default value if omitted
- **-i --client_id [client_id]**
                            Finagle client id to send request with
- **-v --verbose**         Provide detailed logging

#### Includes

As a convenience you can define an environment variable THRIFT_CLI_PATH. This colon delimited list of directories will be used to find thrift files and their dependencies.

Take the following command 

```
thriftcli localhost:9332 MakeTestCall ~/thrift/test/test.thrift -I ~/thrift/dependencies
```

If you had run the following before

```
export THRIFT_CLI_PATH="~/thrift/test:~/thrift/dependencies"
```

this command becomes

```
thriftcli localhost:9332 MakeTestCall test.thrift
```

This variable is most useful for endpoints you call fairly often.

#### Proxy

If you need to access a server behind a proxy, the `--proxy` option allows you to do so:

```
thriftcli server:port Hello.echo Hello.thrift -b '{"name": "World"}' -j --proxy prod-proxy:3128
```

## Examples
```
thriftcli localhost:9090 Calculator.ping ./Calculator.thrift
thriftcli localhost:9090 Calculator.add ./Calculator.thrift --body add_request_body.json
thriftcli localhost:9090 Calculator.doWork ./Calculator.thrift --body '{"work": {"num1": 1, "num2": 3, "op": "ADD"}}'
thriftcli localhost:9090 Calculator.doWork ./Calculator.thrift --body 'Work(num1:1,num2:3,op:ADD)'
thriftcli localhost:9093 Calculator.doWork ./Calculator.thrift --body 'Work(num1:1,num2:3,op:ADD)' --tls
thriftcli localhost:12201 Animals.get ~/Animals.thrift -I ~/included-thrifts/ --body ~/animals_get.json
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

#### Conflicting Method Names

Consider two services, A and B, which are both defined in MyThrift.thrift and declare a method named helloWorld.

Assume you're running a server that implements A.helloWorld.

When using ThriftCLI, both endpoints A.helloWorld and B.helloWorld will execute the running server's implementation of A.helloWorld.

This is due to the nature of Thrift and cannot be checked for prior to execution. The ThriftCLI user is responsible for assuring that the correct helloWorld implementation is called.

#### Keywords

Use of Python keywords in service definitions is not supported by ThriftCLI.

If you provide ThriftCLI with a thrift file that uses a Python keyword, or has a dependency that does, running ThriftCLI will fail.

A full list of Python keywords can be found at https://docs.python.org/2/reference/lexical_analysis.html#keywords.

#### Unions

Unions are not supported right now.

#### Python 2.7

Python 3 is not supported. Due to the dependency we have on Twitter thrift libraries (Python 2 only) upgrading is not straightforward.

## License

    Copyright 2020, Fitbit, Inc.
    Licensed under the Apache License, Version 2.0 (the "License"); you 
    may not use this file except in compliance with the License.
    You may obtain a copy of the License at
          http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software 
    distributed under the License is distributed on an "AS IS" BASIS, 
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and 
    limitations under the License.
