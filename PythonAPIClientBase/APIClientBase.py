import requests
from .Mock import MockClass
import threading
from urllib.parse import urlencode
from .VerboseLogging import VerboseLoggingNullLogClass

class APIClientException(Exception):
  result = None
  def __init__(self, result):
    self.result = result
  def getDescriptionString(self):
    ret = ""
    ret += "Failed API request\n"
    ret += "Request: " + str(self.result.request.method) + ":" + str(self.result.request.url) + "\n"
    ret += "Response: " + str(self.result.status_code) + ":" + self.result.content.decode() + "\n"
    return ret
  def __str__(self):
    return self.getDescriptionString()

class APIClientNotFoundException(APIClientException):
  def __init__(self, result):
    super(APIClientNotFoundException, self).__init__(result)



class APIClientBase():
  mock = None
  baseURL = None
  requestLock = None
  verboseLogging = None

  def __init__(self, baseURL, mock=None, forceOneRequestAtATime=False, verboseLogging=VerboseLoggingNullLogClass()):
    self.verboseLogging = verboseLogging
    if baseURL.endswith("/"):
      raise Exception("baseURL should not contain trailing slash: " + baseURL)

    if mock is None:
      self.mock = MockClass()
    else:
      self.mock = mock

    self.baseURL = baseURL

    if forceOneRequestAtATime:
      self.requestLock = threading.Lock()
    else:
      self.requestLock = None

  def raiseResponseException(self, result):
    if (result.status_code == 404):
      raise APIClientNotFoundException(result)
    raise APIClientException(result)

  def testRegisterNextResponse(self, *args, **kwargs):
    return self.mock.registerNextResponse(*args, **kwargs)
  def testComplete(self):
    return self.mock.testComplete()
  def testGetMockObj(self):
    return self.mock

  #skipLockCheck is used for when the refresh process itself is sending a request
  # Note when updating params to this function, reflect that update in the refresh logic or there will be a refresh bug
  def sendRequest(self, reqFn, url, loginSession, data, origin, injectHeadersFn, postRefreshCall=False, skipLockCheck=False, params=None):
    # url must start with slash
    headers = {}
    if loginSession is not None:
      loginSession.injectHeaders(headers)
    if origin is not None:
      headers["origin"] = origin
    if injectHeadersFn is not None:
      injectHeadersFn(headers)

    if self.baseURL == "MOCK":
      if params is not None:
        if len(params.keys()) > 0:
          url += "?" + urlencode(params)
      return self.mock.returnNextResult(reqFnName=reqFn.__name__, url=url, data=data)

    self.verboseLogging.log_call(
      reqFn=reqFn.__name__,
      url=self.baseURL + url,
      params=params,
      data=data,
      headers=headers,
      postRefreshCall=postRefreshCall
    )

    lockWasObtained = False
    try:
      if self.requestLock is not None:
        if not skipLockCheck:
          if not lockWasObtained:
            self.requestLock.acquire(blocking=True, timeout=-1)
          lockWasObtained = True
      result = reqFn(
        url=self.baseURL + url,
        params=params,
        data=data,
        headers=headers
      )
      if result.status_code == 401:
        if postRefreshCall:
          self.raiseResponseException(result)
        if loginSession is None:
          self.raiseResponseException(result)

        if loginSession.refresh(): #Returns true if loginSession refresh succeeded
          # We sendanother request withou lock checking
          #  when this is complete the local finally will be called
          #  so the lock will be released then
          return self.sendRequest(
            reqFn=reqFn,
            url=url,
            loginSession=loginSession,
            data=data,
            origin=origin,
            injectHeadersFn=injectHeadersFn,
            postRefreshCall=True,
            skipLockCheck=True,
            params=params
          )
        self.raiseResponseException(result)
    finally:
      if lockWasObtained:
        self.requestLock.release()

    self.verboseLogging.log_result(result)

    return result

  def sendGetRequest(self, url, loginSession, origin=None, injectHeadersFn=None, params=None):
    return self.sendRequest(reqFn=requests.get, url=url, loginSession=loginSession, data=None, origin=origin, injectHeadersFn=injectHeadersFn, params=params)

  def sendPostRequest(self, url, loginSession, data, origin=None, injectHeadersFn=None, params=None):
    return self.sendRequest(reqFn=requests.post, url=url, loginSession=loginSession, data=data, origin=origin, injectHeadersFn=injectHeadersFn, params=params)

  def sendPutRequest(self, url, loginSession, data, origin=None, injectHeadersFn=None, params=None):
    return self.sendRequest(reqFn=requests.put, url=url, loginSession=loginSession, data=data, origin=origin, injectHeadersFn=injectHeadersFn, params=params)

  def sendDeleteRequest(self, url, loginSession, data=None, origin=None, injectHeadersFn=None, params=None):
    return self.sendRequest(reqFn=requests.delete, url=url, loginSession=loginSession, data=data, origin=origin, injectHeadersFn=injectHeadersFn, params=params)

  def sendHeadRequest(self, url, loginSession, data=None, origin=None, injectHeadersFn=None, params=None):
    return self.sendRequest(reqFn=requests.head, url=url, loginSession=loginSession, data=data, origin=origin, injectHeadersFn=injectHeadersFn, params=params)

  def sendOptionsRequest(self, url, loginSession, data=None, origin=None, injectHeadersFn=None, params=None):
    return self.sendRequest(reqFn=requests.options, url=url, loginSession=loginSession, data=data, origin=origin, injectHeadersFn=injectHeadersFn, params=params)
