import threading
import sys
import time
import SocketServer

PORT = 389

class BaseRequestHandler(SocketServer.BaseRequestHandler):

    def get_data(self):
        raise NotImplementedError

    def send_data(self, data):
        raise NotImplementedError

    def handle(self):
        # print('[+] handle it')
        request = self.get_data()
        print('[+] Request\n{0}'.format(repr(request)))
        request_id = request[8]
        response = "\x30\x84\x00\x00\x00\x86\x02\x01_PLACEHOLDER_\x64\x84\x00\x00\x00\x7d\x04\x00\x30\x84\x00\x00\x00\x75\x30\x84\x00\x00\x00\x6f\x04\x08\x6e\x65\x74\x6c\x6f\x67\x6f\x6e\x31\x84\x00\x00\x00\x5f\x04\x5d\x17\x00\x00\x00\xfd\xf3\x01\x00\x3f\x0a\xf9\x25\xf2\x1d\x60\x4d\x87\x2b\xbd\x59\xdf\x1f\x43\xc7\x04\x63\x6f\x72\x70\x05\x6c\x6f\x63\x61\x6c\x00\xc0\x18\x04\x44\x43\x30\x31\xc0\x18\x04\x43\x4f\x52\x50\x00\x04\x44\x43\x30\x31\x00\x00\x17\x44\x65\x66\x61\x75\x6c\x74\x2d\x46\x69\x72\x73\x74\x2d\x53\x69\x74\x65\x2d\x4e\x61\x6d\x65\x00\xc0\x3a\x05\x00\x00\x00\xff\xff\xff\xff\x30\x84\x00\x00\x00\x10\x02\x01_PLACEHOLDER_\x65\x84\x00\x00\x00\x07\x0a\x01\x00\x04\x00\x04\x00"
        response = response.replace('_PLACEHOLDER_', request_id)
        print('[+] Response\n{0}'.format(repr(response)))
        self.send_data(response)


class UDPRequestHandler(BaseRequestHandler):
    def get_data(self):
        print('[+] Get Data')
        return self.request[0].strip()

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)


if __name__ == '__main__':
    print "Starting nameserver..."

    servers = [
        SocketServer.ThreadingUDPServer(('', PORT), UDPRequestHandler)
    ]
    for s in servers:
        thread = threading.Thread(target=s.serve_forever)  # that thread will start one more thread for each request
        thread.daemon = True  # exit the server thread when the main thread terminates
        thread.start()
        print "%s server loop running in thread: %s" % (s.RequestHandlerClass.__name__[:3], thread.name)

    try:
        while 1:
            time.sleep(1)
            sys.stderr.flush()
            sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    finally:
        for s in servers:
            s.shutdown()