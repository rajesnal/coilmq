#
# Copyright 2009 Hans Lellelid
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Entrypoint for starting the application.
"""
__authors__ = [
  '"Hans Lellelid" <hans@xmpl.org>',
]
from optparse import OptionParser

from coilmq.config import config, init_config, resolve_object
from coilmq.topic import TopicManager
from coilmq.queue import QueueManager
from coilmq.store.memory import MemoryQueue
from coilmq.scheduler import FavorReliableSubscriberScheduler, RandomQueueScheduler    
from coilmq.server.socketserver import ThreadedStompServer

def server_from_config(cfg=None):
    """
    Gets a configured L{coilmq.server.StompServer} from specified config.
    
    If config is None, global L{coilmq.config.config} var will be used instead.
    
    @param cfg: A C{ConfigParser.ConfigParser} instance with loaded config values.
    @type cfg: C{ConfigParser.ConfigParser}
    
    @return: The configured StompServer.
    @rtype: L{coilmq.server.StompServer}
    """
    global config
    
    queue_store_class = resolve_object(config.get('coilmq', 'queue_store_class'))
    subscriber_scheduler_class = resolve_object(config.get('coilmq', 'subscriber_scheduler_class'))
    queue_scheduler_class = resolve_object(config.get('coilmq', 'queue_scheduler_class'))
    
    server = ThreadedStompServer((config.get('coilmq', 'listen_addr'), config.getint('coilmq', 'listen_port')),
                                 queue_manager=QueueManager(store=queue_store_class(),
                                                            subscriber_scheduler=subscriber_scheduler_class(),
                                                            queue_scheduler=queue_scheduler_class()),
                                 topic_manager=TopicManager())
    return server

def main():
    """ Start the socket server. """

    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config_file",
                      help="Read configuration from FILE. (CLI options override config file.)", metavar="FILE")
    
    parser.add_option("-b", "--host", dest="listen_addr",
                      help="Listen on specified address (default 0.0.0.0)", metavar="ADDR")
    
    parser.add_option("-p", "--port", dest="listen_port",
                      help="Listen on specified port (default 61613)", type="int", metavar="PORT")
    
    # TODO: Add other options
    #        - daemonize
    #        -- pidfile
    #        -- guid
    #        -- uid
    
    (options, args) = parser.parse_args()
    
    init_config(options.config_file)
    
    if options.listen_addr is not None:
        config.set('coilmq', 'listen_addr', options.listen_addr)
        
    if options.listen_port is not None:
        config.set('coilmq', 'listen_port', options.listen_port)
    
    server = server_from_config()
    server.serve_forever()
    
if __name__ == '__main__':
    main()