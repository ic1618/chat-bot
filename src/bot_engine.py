from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Union

class DefaultOptions:
    """
    Provides methods and default options for financial tools selection.

    This class offers methods for handling default messages and contains
    default options such as 'Menu' and 'Go back'.
    """
    _main_menu = {'Menu': None, 'Go back': None}

    @staticmethod
    def default_msg(msg: str) -> List[Union[str, List[str]]]:
        """
        Generates a message for the user along with a list of default options.

        This method returns a list containing the specified message for the user
        and a list of default options, allowing the user to select from them.
        
        :param msg: The message to be displayed to the user.
        :return: A list containing the message and a list of default options.
        """
        return [msg, list(DefaultOptions.main_menu().keys())]
    
    @staticmethod
    def main_menu() -> Dict[str, Any]:
        return DefaultOptions._main_menu


class Node(ABC):
    """
    Abstract base class for nodes in the decision tree.

    This class defines common functionality for all types of nodes
    in the decision trie.
    """
    def __init__(self, options: Dict[str, Any]) -> None:
        self._all_options = options

    @property
    def all_options(self) -> Dict[str, Any]:
        """
        Gets all the options available for the current node.

        This property returns a dictionary containing all the options for the
        current node, including both the main options (e.g., list of stock exchanges,
        list of stocks) and default options (e.g., 'Menu' and 'Go back').

        :return: A dictionary containing all the options.
        """
        return self._all_options

    def get_next_node(self, selection: str) -> Any:
        if selection not in self.all_options:
            raise KeyError
        
        return self._all_options[selection]

    def _construct_response(self, core_msg: str, main_opts: List[str], *default_opts: List[Union[str, List[str]]]) -> List[Union[str, List[str]]]:
        """
        Helper function to construct response messages for different nodes in the decision trie (e.g.
        stock exchange selected response, welcome message response, stock selected)
        """
        response = [core_msg]

        if not isinstance(main_opts, List):
            raise TypeError(f'Wrong type for options. Expected "List", Actual "{type(main_opts)}"')

        if main_opts:
            response.append(main_opts)

        if default_opts:
            response.extend(*default_opts)

        return response

    @abstractmethod
    def _json_parser(self, json_data: Dict[str, Any]) -> None:
        """
        Parses JSON data to create objects representing financial tools.

        This method is used to create objects nested in the JSON for
        different financial tools (e.g., stock exchange, stock).
        """
        pass

    @abstractmethod
    def print_response(self) -> List[Union[str, List[str]]]:
        pass


class Source(Node):
    """
    Represents the source node in the decision trie.

    This node points to a list of stock exchanges.
    """

    def __init__(self, list_objs: List[Dict[str, Any]]) -> None:
        try:
            super().__init__(self._json_parser(list_objs))
        except KeyError as e:
            raise KeyError(f"Could not initialise Source object: {e}")

    def _json_parser(self, list_objs: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            markets = [StockExchange(json_obj) for json_obj in list_objs]
            return {market.name: market for market in markets}
        except KeyError as e:
            raise KeyError(f"Error parsing JSON object: {e}")
        
    def print_response(self) -> List[Union[str, List[str]]]:
        core_msg = "Please select a stock exchange:"
        return super()._construct_response(core_msg, list(self.all_options.keys()))


class StockExchange(Node):
    """
    Represents a stock exchange node in the decision trie.

    This node provides a list of stock options to select from.
    """

    _msg = "If you do not wish to proceed, then please select one of the following:"

    def __init__(self, json_obj: Dict[str, Any]) -> None:
        name, options = "", {}
        try:
            name, options = self._json_parser(json_obj)
        except KeyError as e:
            raise KeyError(f"Could not initialise StockExchange object: {e}")

        self._name = name
        self._main_options = options

        all_options = dict(options)
        default_menu = dict(DefaultOptions.main_menu())
        all_options.update(default_menu)
        super().__init__(all_options)

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def main_options(self) -> Dict[str, Any]:
        return self._main_options

    def _json_parser(self, json_data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        try:
            name = json_data['stockExchange']
            stocks_list = [Stock(stock) for stock in json_data['topStocks']]
            return name, {stock.name: stock for stock in stocks_list}
        except KeyError as e:
            raise KeyError(f"Error parsing JSON object: {e}")

    def print_response(self) -> List[Union[str, List[str]]]:
        core_msg = "You selected {}. Please select a stock:".format(self.name)
        return super()._construct_response(core_msg, list(self.main_options.keys()), DefaultOptions.default_msg(StockExchange._msg))


class Stock(Node):
    """
    Represents a stock node in the decision trie.

    This node provides information about a selected stock, including its name and price.
    """

    _msg = "Please choose one of the following:"

    def __init__(self, json_obj: Dict[str, Any]) -> None:
        super().__init__(dict(DefaultOptions.main_menu()))
        self._name = None
        self._price = None
        try:
            self._name, self._price = self._json_parser(json_obj)
        except KeyError as e:
            raise KeyError(f"Could not initialise Stock object: {e}")

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def price(self) -> float:
        return self._price

    def _json_parser(self, json_data: Dict[str, Any]) -> Tuple[str, float]:
        try:
            name, price = json_data['stockName'], json_data['price']
            return name, price
        except KeyError as e:
            raise KeyError(f"Error parsing JSON object: {e}")

    def print_response(self) -> List[Union[str, List[str]]]:
        core_msg = "Stock price of {} is {}".format(self.name, self.price)
        return super()._construct_response(core_msg, [], DefaultOptions.default_msg(Stock._msg))


class Trie:
    """
    Represents a trie structure for decision-making in the chatbot.

    This class creates a trie connection between all possible states that the chatbot 
    can reach. Each state is represented by a node. Every node points to possible 
    states(or options) that can be selected at that moment.
    """

    def __init__(self, json_data: List[Dict[str, Any]]) -> None:
        self._source = Source(json_data)
        self._current_node = self._source

    @property
    def current_node(self) -> Node:
        return self._current_node

    def next_node(self, selected: str) -> "Trie":
        """
        Moves to the next node based on the selected option.

        This method traverses the trie in a graph traversal manner
        and prints the response associated with the new node.
        """
        if selected not in self.get_options():
            raise OptionError(f"Selected option '{selected}' does not exist")

        try:
            parent = self._current_node
            self._current_node = self._current_node.get_next_node(selected)
            self._init_defaults(parent)
        except KeyError or TypeError as e:
            raise TrieError(f"Could not initialise trie: {e}")
        return self
    
    def _init_defaults(self, parent: Node) -> None:
        if self._current_node == self._source:
            return
        
        if self._current_node.all_options['Menu']:
            return
        
        self._current_node._all_options.update({'Menu': self._source, 'Go back': parent})

    def get_options(self) -> Dict[str, Any]:
        return self._current_node.all_options

class TrieError(Exception):
    """
    TrieError is used to represent the errors raised during the initialisation of the trie/nodes.
    """
    pass

class OptionError(Exception):
    """
    OptionError is raised when a selected option could not be found in the available options.
    """
    pass
