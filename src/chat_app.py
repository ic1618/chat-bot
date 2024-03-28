from src.bot_engine import Trie, TrieError, OptionError

class ChatApp:
    def __init__(self, json_data):
        self.trie_node = Trie(json_data)
        self.start_flag = True

    def get_welcome_message(self):
        return "Hello! Welcome to LSEG. I am here to help you."

    def get_unavailable_message(self):
        return "Sorry, this option is not available. Please try again."

    def get_fail_message(self):
        return "Sorry, we encountered an issue. Please try again later."

    def get_chat_response(self, text):
        if self.start_flag:
            self.start_flag = False
            return self.formulate_response(self.trie_node.current_node.print_response(), self.get_welcome_message())

        try:
            self.trie_node = self.trie_node.next_node(text)
        except OptionError as opt_error:
            print(opt_error)
            return self.formulate_response(self.trie_node.current_node.print_response(), self.get_unavailable_message())
        except TrieError as trie_error:
            print(trie_error)
            return self.get_fail_message()

        return self.formulate_response(self.trie_node.current_node.print_response())

    def formulate_response(self, options_msg, *additional_msg):
        response = []
        if additional_msg:
            response.append(*additional_msg)

        response.extend(options_msg)
        return response