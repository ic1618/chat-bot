from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Union

class DefaultOptions:
    _main_menu = {'Menu': None, 'Go back': None}

    @staticmethod
    def default_msg(msg: str) -> List[Union[str, List[str]]]:
        return [msg, list(DefaultOptions.main_menu().keys())]
    
    @staticmethod
    def main_menu() -> Dict[str, Any]:
        return DefaultOptions._main_menu


class Node(ABC):
    def __init__(self, options: Dict[str, Any]) -> None:
        self._all_options = options

    @property
    def all_options(self) -> Dict[str, Any]:
        return self._all_options

    def get_next_node(self, selection: str) -> Any:
        if selection not in self.all_options:
            raise KeyError
        
        return self._all_options[selection]

    def _construct_response(self, core_msg: str, main_opts: List[str], *default_opts: List[Union[str, List[str]]]) -> List[Union[str, List[str]]]:
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
        pass

    @abstractmethod
    def print_response(self) -> List[Union[str, List[str]]]:
        pass


class Source(Node):
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
    def __init__(self, json_data: List[Dict[str, Any]]) -> None:
        self._source = Source(json_data)
        self._current_node = self._source

    @property
    def current_node(self) -> Node:
        return self._current_node

    def next_node(self, selected: str) -> "Trie":
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
    pass

class OptionError(Exception):
    pass
