

class VerboseLoggingBaseClass():
    def log_call(
        reqFn,
        url,
        params,
        data,
        headers,
        postRefreshCall
    ):
        pass

    def log_result(self, result):
        pass

class VerboseLoggingNullLogClass(VerboseLoggingBaseClass):
    # base class already does nothing
    pass

class VerboseLoggingOutputAllClass(VerboseLoggingBaseClass):
    call = None
    result = None
    include_data = None

    def __init__(self, call=True, include_data=True, result=True):
        self.call = call
        self.result = result
        self.include_data = include_data

    def log_call(
        reqFn,
        url,
        params,
        data,
        headers,
        postRefreshCall
    ):
        if not self.call:
            return
        print("------------------")
        print("API Client Call")
        print("------------------")
        print(reqFn, url)
        print("params", params)
        print("headers:")
        for header in headers:
            print("  ", header + ":", headers[header])
        if self.include_data:
            print("data", data)
        print("------------------")
        print("")

    def log_result(self, result):
        if not self.result:
            return
        print("------------------")
        print("API Client Response")
        print("------------------")
        print(result)
        print("------------------")
        print("")
