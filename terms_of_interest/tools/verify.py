from ..schemas import Tweet


class ResultsVerifier:
    def load_messages(self, tweets_file):
        messages = {}
        for line in tweets_file:
            tweet = Tweet.parse_raw(line)
            messages[tweet.message_id] = tweet.text.lower()
        return messages

    def verify(self, results_file):
        for idx, line in enumerate(results_file):
            term, message_id = line.rstrip().split(", ")
            if not term in self.messages[message_id]:
                self.print_error(idx, term, message_id)

    def print_error(self, line_num, term, message_id):
        print(
            f"[!] Line: {line_num} Term: '{term}' not found in message_id: '{message_id}'"
        )
        print(f"    Message Text: '{self.messages[message_id]}'")

    def run(self, tweets_file, results_file):
        self.messages = self.load_messages(tweets_file)
        self.verify(results_file)
        print(f"Verified {len(self.messages)} messages!")
