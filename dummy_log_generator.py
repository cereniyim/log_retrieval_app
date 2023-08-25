import logging
import random

# Set up logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - User:%(user_id)s - %(message)s",
)


# error metrics
error_metrics = ["ROC-AUC", "F1", "Precision", "Recall", "Sensitivity", "Specificity"]

# user IDs
user_ids = [1, 2, 3, 4, 5]


class DummyLogGenerator:
    def __init__(
        self,
        user_ids: list[int],
        error_metrics: list[str],
        log_levels: list[str] = None,
    ):
        self._user_ids = user_ids
        self._error_metrics = error_metrics
        self._log_levels = log_levels or ["info", "error", "debug"]

    def generate(self):
        log_level = random.choice(self._log_levels)
        user_id = random.choice(self._user_ids)
        error_metric = random.choice(self._error_metrics)
        random_word = self._generate_random_word()
        message = self._generate_log_message(user_id, error_metric, random_word)

        if log_level == "info":
            logging.info(message, extra={"user_id": user_id})
        elif log_level == "error":
            logging.error(message, extra={"user_id": user_id})
        elif log_level == "debug":
            logging.debug(message, extra={"user_id": user_id})
        return {"log_level": log_level, "user_id": user_id, "message": message}

    def _generate_log_message(self, user_id: int, error_metric: str, random_word: str):
        error = random.random()
        return f"Validated a new model, {random_word}. User: {user_id}, {error_metric}: {error}"

    def _generate_random_word(self):
        random_sentence = "Lorem ipsum dolor sit amet consectetur adipiscing elit Maecenas ullamcorper convallis leo sit amet feugiat ligula viverra eu"
        return random.choice(random_sentence.split())


# Initialize and use the DummyLogGenerator class
# dummy_log_generator = DummyLogGenerator(user_ids, error_metrics)
# dummy_log_generator.generate()
