#!/usr/bin/python3

from zocp import ZOCP
import socket
import logging

class SubscriptionMakerNode(ZOCP):
    # Constructor
    def __init__(self, nodename=""):
        self.nodename = nodename
        self.subscribe = False
        self.subscriber_peer = None
        self.subscribee_peer = None
        super().__init__()

    def run(self):
        self.set_name(self.nodename)
        self.register_bool("Subscribe 'My String'", self.subscribe, 'rw')
        self.start()
        super().run()
        
    def on_peer_enter(self, peer, name, *args, **kwargs):
        split_name = name.split("@",1)
        if split_name[0] == 'subscribee':
            self.subscribee_peer = peer
            self.update_subscription()

        elif split_name[0] == 'subscriber':
            self.subscriber_peer = peer
            self.update_subscription()

    def on_modified(self, peer, name, data, *args, **kwargs):
        if self._running and peer:
            for key in data:
                if 'value' in data[key]:
                    self.receive_value(key)

    def on_peer_signaled(self, peer, name, data, *args, **kwargs):
        if self._running and peer:
            self.receive_value(data[0])

    def receive_value(self, key):
        new_value = self.capability[key]['value']

        if key == "Subscribe 'My String'":
            if new_value != self.subscribe:
                self.subscribe = new_value
                self.update_subscription()

    def update_subscription(self):
        if self.subscribee_peer is not None and self.subscriber_peer is not None:
            if self.subscribe:
                self.signal_subscribe(self.subscribee_peer, "My String", self.subscriber_peer, "My String")
            else:
                self.signal_unsubscribe(self.subscribee_peer, "My String", self.subscriber_peer, "My String")

        
if __name__ == '__main__':
    zl = logging.getLogger("zocp")
    zl.setLevel(logging.DEBUG)

    z = SubscriptionMakerNode("3rdparty@%s" % socket.gethostname())
    z.run()
    print("FINISH")
