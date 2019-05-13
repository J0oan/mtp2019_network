from . import cte
from .node import Node
from .utils import get_args, process_config, get_file


def start(role, led, team_config):
    """

    :param role: String with the role of device (tx or rx)
    :param led: Object of a Class with methods to change led status
    :param team_config: Bunch object with the configuration related with each team
    :return:
    """

    led.network_starting()

    config = team_config
    try:
        # Get arguments
        args = get_args()
        # Get config file from arguments
        config.update(process_config(args.config))
    except:
        print("missing or invalid arguments")
        exit(0)

    if role == 'tx':
        led.network_tx()
        file = get_file(config)
    else:
        led.network_rx()
        file = False

    # Create node entity according to config and pass file if it is possible.
    # TODO is it necessary to pass led to Node for use it there?
    node = Node(config, file)

    loop = True
    # Main loop
    while loop:

        # Check if packet received
        node.check_receiver()

        if node.state is cte.BROADCAST_FLOODING:
            # If node state is broadcast flooding set retransmission of state
            # and begin broadcast transmission
            node.retransmission = config.nDiscovery
            node.broadcast_flooding()

        elif node.state is cte.CHOOSE_RECEIVER:
            # If node state is choose receiver, execute its function
            node.choose_receiver()

        elif node.state is cte.SEND_PACKET:
            # If node state is send data packet set retransmission for this packet
            # and start transmission
            node.retransmission = config.nData
            node.send_packets()

        elif node.state is cte.RECEIVE_DATA:
            # If the node has received a new data packet send ack
            node.receive_packets()

        elif node.state is cte.PASS_TOKEN:
            # If there is a successor to pass the token
            node.retransmission = config.nToken
            node.pass_token()

        elif node.state is cte.RETURN_TOKEN:
            # If this network branch is completed return token
            node.retransmission = config.nToken
            node.return_token()

        elif node.state is cte.CHOOSE_TOKEN:
            # State to select a successor of the token
            node.choose_token_successor()

        elif node.state is cte.END:
            # State to send end of protocol
            node.send_end()

        elif node.state is cte.ERROR_END:
            led.network_error()
            node.transmitter.powerDown()
            node.receiver.powerDown()
            loop = False

        elif node.state is cte.OFF:
            led.network_success()
            loop = False

# TODO definar todos los estados led necesario y cada equipo implementarlos en su main,
#  de momento se han definido:
#  - led.network_starting()
#  - led.network_tx()
#  - led.network_rx()
#  - led.network_error()
#  - led.network_success()
