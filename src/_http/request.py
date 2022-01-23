from io import BufferedReader, BytesIO


class RequestError(Exception):
    def __init__(self, *args, error_code=400) -> None:
        super().__init__(*args)
        self.error_code = error_code


class BadRequestError(RequestError):
    pass


class RequestNotImplementedError(RequestError):
    pass


class Request:
    TERM = '\r\n'
    def __init__(self, data) -> None:
        self.headers = {}
        self._body = BytesIO(data)
        self.msg = None
        self._parse_header()
    
    def _parse_header(self):
        with BufferedReader(self._body) as body:
            request_line = body.readline().decode('utf-8')
            method, path, proto = request_line.rstrip(self.TERM).split(' ') 

            self.check_request_line(method, path, proto)
            self.headers['Method'] = method
            self.headers['Path'] = path
            self.headers['Proto'] = ''

            for hdr in body:
                hdr = hdr.decode('utf-8').rstrip(self.TERM)
                if len(hdr) < 1:
                    break
                field = hdr.split(':')
                if len(field) > 1:
                    key_len = len(field[0])
                    self.headers[field[0]] = ''.join(tok for tok in hdr[key_len+1:])
            self.msg = body.read().decode('utf-8').rstrip(self.TERM)
    
    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, hdr):
        if not hdr:
            raise BadRequestError('Invalid request') 
        self._headers = hdr
    
    def check_request_line(self, method, path, proto):
        err = BadRequestError('Invalid request')
        if not method:
            raise err
        
        if not path:
            raise err

        if not proto:
            raise err


class Response:
    def __init__(self, client_conn, request) -> None:
        pass