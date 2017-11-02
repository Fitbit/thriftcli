namespace java com.fitbit.thriftcli.thriftjava

/*
    This sample thrift file is used for testing.
    If changes are made, be sure to regenerate the classes ("thrift -r -gen py Sample.thrift")
    and move them under the directory data/generated
 */
struct SampleResponse {
    1: optional string message

    2: optional set<string> tags
}
