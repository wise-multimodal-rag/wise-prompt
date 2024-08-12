"""Contains classes for querying large language models."""
import logging
import os
import time
from abc import ABC, abstractmethod
from itertools import chain

from openai import OpenAI
from tqdm import tqdm


gpt_costs_per_thousand = {
    'davinci': 12.00,
    'gpt-4o-mini': 0.0150,
    'gpt-3.5-turbo-instruct': 1.50,
    'got-3.5-turbo': 3.00,
}


def model_from_config(config, disable_tqdm=True):
    """Returns a model based on the config."""
    model_type = config["name"]
    if model_type == "GPT_forward":
        return GPT_Forward(config, disable_tqdm=disable_tqdm)
    elif model_type == "GPT_insert":
        return GPT_Insert(config, disable_tqdm=disable_tqdm)
    raise ValueError(f"Unknown model type: {model_type}")


class LLM(ABC):
    """Abstract base class for large language models."""

    @abstractmethod
    def generate_text(self, prompt, n):
        """Generates text from the model.
        Parameters:
            prompt: The prompt to use. This can be a string or a list of strings.
            n:
        Returns:
            A list of strings.
        """
        pass

    @abstractmethod
    def log_probs(self, text, log_prob_range):
        """Returns the log probs of the text.
        Parameters:
            text: The text to get the log probs of. This can be a string or a list of strings.
            log_prob_range: The range of characters within each string to get the log_probs of. 
                This is a list of tuples of the form (start, end).
        Returns:
            A list of log probs.
        """
        pass


class GPT_Forward(LLM):
    """Wrapper for GPT-3."""

    def __init__(self, config, needs_confirmation=False, disable_tqdm=True):
        """Initializes the model."""
        self.config = config
        self.needs_confirmation = needs_confirmation
        self.disable_tqdm = disable_tqdm
        self.client = OpenAI()

    def confirm_cost(self, texts, n, max_tokens):
        total_estimated_cost = 0
        for text in texts:
            total_estimated_cost += gpt_get_estimated_cost(self.config, text, max_tokens) * n
        logging.info(f"Estimated cost: ${total_estimated_cost:.2f}")
        # Ask the user to confirm in the command line
        if os.getenv("LLM_SKIP_CONFIRM") is None:
            confirm = input("Continue? (y/n) ")
            if confirm != 'y':
                raise Exception("Aborted.")

    def auto_reduce_n(self, fn, prompt, n):
        """Reduces n by half until the function succeeds."""
        try:
            return fn(prompt, n)
        except BatchSizeException as e:
            if n == 1:
                raise e
            return self.auto_reduce_n(fn, prompt, n // 2) + self.auto_reduce_n(fn, prompt, n // 2)

    def generate_text(self, prompt, n):
        if not isinstance(prompt, list):
            prompt = [prompt]
        if self.needs_confirmation:
            self.confirm_cost(prompt, n, self.config['gpt_config']['max_tokens'])
        batch_size = self.config['batch_size']
        prompt_batches = [prompt[i:i + batch_size] for i in range(0, len(prompt), batch_size)]
        if not self.disable_tqdm:
            logging.debug(f"[{self.config['name']}] Generating {len(prompt) * n} completions, "
                          f"split into {len(prompt_batches)} batches of size {batch_size * n}")
        texts = []
        for prompt_batch in tqdm(prompt_batches, disable=self.disable_tqdm):
            texts += self.auto_reduce_n(self.__generate_text, prompt_batch, n)
        return texts

    def complete(self, prompt, n):
        """Generates text from the model and returns the log prob data."""
        if not isinstance(prompt, list):
            prompt = [prompt]
        batch_size = self.config['batch_size']
        prompt_batches = [prompt[i:i + batch_size] for i in range(0, len(prompt), batch_size)]
        if not self.disable_tqdm:
            logging.debug(
                f"[{self.config['name']}] Generating {len(prompt) * n} completions, "
                f"split into {len(prompt_batches)} batches of size {batch_size * n}")
        res = []
        for prompt_batch in tqdm(prompt_batches, disable=self.disable_tqdm):
            res += self.__complete(prompt_batch, n)
        return res

    def log_probs(self, text, log_prob_range=None):
        """Returns the log probs of the text."""
        if not isinstance(text, list):
            text = [text]
        if self.needs_confirmation:
            self.confirm_cost(text, 1, 0)
        batch_size = self.config['batch_size']
        text_batches = [text[i:i + batch_size] for i in range(0, len(text), batch_size)]
        if log_prob_range is None:
            log_prob_range_batches = [None] * len(text)
        else:
            assert len(log_prob_range) == len(text)
            log_prob_range_batches = [log_prob_range[i:i + batch_size] for i in
                                      range(0, len(log_prob_range), batch_size)]
        if not self.disable_tqdm:
            logging.debug(
                f"[{self.config['name']}] Getting log probs for {len(text)} strings, "
                f"split into {len(text_batches)} batches of (maximum) size {batch_size}")
        log_probs = []
        tokens = []
        for text_batch, log_prob_range in tqdm(
                list(zip(text_batches, log_prob_range_batches)), disable=self.disable_tqdm):
            log_probs_batch, tokens_batch = self.__log_probs(text_batch, log_prob_range)
            log_probs += log_probs_batch
            tokens += tokens_batch
        return log_probs, tokens

    def __generate_text(self, prompts, n):
        """Generates text from the model."""
        config = self.config['gpt_config'].copy()
        config['n'] = n
        # If there are any [APE] tokens in the prompts, remove them
        for i in range(len(prompts)):
            prompts[i] = prompts[i].replace('[APE]', '').strip()
        responses = []
        response = None
        while response is None:
            try:
                for prompt in prompts:
                    response = self.client.chat.completions.create(**config, messages=[{"role": "user", "content": prompt}])
                    responses.append([response.choices[i].message.content for i in range(len(response.choices))])
            except Exception as e:
                if 'is greater than the maximum' in str(e):
                    raise BatchSizeException()
                logging.debug(f'Retrying... ({e})')
                time.sleep(5)
        res = list(chain.from_iterable(responses))
        logging.info(f"Generated Texts: {res}")
        return res

    def __complete(self, prompts, n):
        """Generates text from the model and returns the log prob data."""
        config = self.config['gpt_config'].copy()
        config['n'] = n
        # If there are any [APE] tokens in the prompts, remove them
        for i in range(len(prompts)):
            prompts[i] = prompts[i].replace('[APE]', '').strip()
        responses = []
        response = None
        while response is None:
            try:
                for prompt in prompts:
                    response = self.client.chat.completions.create(**config, messages=[{"role": "user", "content": prompt}])
                    responses.append(response)
            except Exception as e:
                logging.debug(f'Retrying... ({e})')
                time.sleep(5)
        return [res.choices[0] for res in responses]

    def __log_probs(self, texts, log_prob_range=None):
        """Returns the log probs of the text."""
        if not isinstance(texts, list):
            texts = [texts]
        if log_prob_range is not None:
            for i in range(len(texts)):
                lower_index, upper_index = log_prob_range[i]
                assert lower_index < upper_index
                assert lower_index >= 0
                assert upper_index - 1 < len(texts[i])
        config = self.config['gpt_config'].copy()
        config['logprobs'] = True
        texts = [f'\n{texts[i]}' for i in range(len(texts))] if isinstance(texts, list) else f'\n{texts}'
        responses = []
        response = None
        while response is None:
            try:
                for prompt in texts:
                    response = self.client.chat.completions.create(**config, messages=[{"role": "user", "content": prompt}])
                    responses.append(response)
            except Exception as e:
                logging.debug(f'Retrying... ({e})')
                time.sleep(3)
        log_probs = []
        tokens = []
        offsets = []
        for response in responses:
            content_ = response.choices[0].logprobs.content
            # log_probs.append([con['logprob'] for con in content_][1:])
            log_prob = [con.logprob for con in content_]
            token = [con.token for con in content_]
            offset = [0]
            for i in range(1, len(content_)):
                offset.append(offset[i - 1] + len(content_[i].token))
            if log_prob and token and offset:
                log_probs.append(log_prob)
                # tokens.append([con['token'] for con in content_][1:])
                tokens.append(token)
                # offsets.append(offset[1:])
                offsets.append(offset)

        # Subtract 1 from the offsets to account for the newline
        for i in range(len(offsets)):
            offsets[i] = [offset - 1 for offset in offsets[i]]
        if log_prob_range is not None:
            # First, we need to find the indices of the tokens in the log probs
            # that correspond to the tokens in the log_prob_range
            for i in range(len(log_probs)):
                lower_index, upper_index = self.get_token_indices(offsets[i], log_prob_range[i])
                log_probs[i] = log_probs[i][lower_index:upper_index]
                tokens[i] = tokens[i][lower_index:upper_index]
        return log_probs, tokens

    def get_token_indices(self, offsets, log_prob_range):
        """Returns the indices of the tokens in the log probs that correspond to the tokens in the log_prob_range."""
        # For the lower index, find the highest index that is less than or equal to the lower index
        lower_index = 0
        for i in range(len(offsets)):
            if offsets[i] <= log_prob_range[0]:
                lower_index = i
            else:
                break
        upper_index = len(offsets)
        for i in range(len(offsets)):
            if offsets[i] >= log_prob_range[1]:
                upper_index = i
                break
        return lower_index, upper_index


class GPT_Insert(LLM):

    def __init__(self, config, needs_confirmation=False, disable_tqdm=True):
        """Initializes the model."""
        self.config = config
        self.needs_confirmation = needs_confirmation
        self.disable_tqdm = disable_tqdm
        self.client = OpenAI()

    def confirm_cost(self, texts, n, max_tokens):
        total_estimated_cost = 0
        for text in texts:
            total_estimated_cost += gpt_get_estimated_cost(
                self.config, text, max_tokens) * n
        logging.info(f"Estimated cost: ${total_estimated_cost:.2f}")
        # Ask the user to confirm in the command line
        if os.getenv("LLM_SKIP_CONFIRM") is None:
            confirm = input("Continue? (y/n) ")
            if confirm != 'y':
                raise Exception("Aborted.")

    def auto_reduce_n(self, fn, prompt, n):
        """Reduces n by half until the function succeeds."""
        try:
            return fn(prompt, n)
        except BatchSizeException as e:
            if n == 1:
                raise e
            return self.auto_reduce_n(fn, prompt, n // 2) + self.auto_reduce_n(fn, prompt, n // 2)

    def generate_text(self, prompt, n):
        if not isinstance(prompt, list):
            prompt = [prompt]
        if self.needs_confirmation:
            self.confirm_cost(
                prompt, n, self.config['gpt_config']['max_tokens'])
        batch_size = self.config['batch_size']
        assert batch_size == 1
        prompt_batches = [prompt[i:i + batch_size] for i in range(0, len(prompt), batch_size)]
        if not self.disable_tqdm:
            logging.debug(f"[{self.config['name']}] Generating {len(prompt) * n} completions, "
                          f"split into {len(prompt_batches)} batches of (maximum) size {batch_size * n}")
        text = []
        for prompt_batch in tqdm(prompt_batches, disable=self.disable_tqdm):
            text += self.auto_reduce_n(self.__generate_text, prompt_batch, n)
        return text

    def log_probs(self, text, log_prob_range=None):
        raise NotImplementedError

    def __generate_text(self, prompt, n):
        """Generates text from the model."""
        config = self.config['gpt_config'].copy()
        config['n'] = n
        # Split prompts into prefixes and suffixes with the [APE] token (do not include the [APE] token in the suffix)
        # prefix = prompt[0].split('[APE]')[0]
        suffix = prompt[0].split('[APE]')[1]
        response = None
        while response is None:
            try:
                # response = client.chat.completions.create(**config, messages=[{"role": "user", "content": prompt}], suffix=suffix)
                response = self.client.chat.completions.create(**config, messages=[{"role": "user", "content": prompt}])
            except Exception as e:
                logging.debug(f'Retrying... ({e})')
                time.sleep(5)

        # Remove suffix from the generated text
        texts = [response['choices'][i]['text'].replace(suffix, '') for i in range(len(response['choices']))]
        return texts


def gpt_get_estimated_cost(config, prompt, max_tokens):
    """Uses the current API costs/1000 tokens to estimate the cost of generating text from the model."""
    # Get rid of [APE] token
    prompt = prompt.replace('[APE]', '')
    # Get the number of tokens in the prompt
    n_prompt_tokens = len(prompt) // 4
    # Get the number of tokens in the generated text
    total_tokens = n_prompt_tokens + max_tokens
    engine = config['gpt_config']['model'].split('-')[1]
    costs_per_thousand = gpt_costs_per_thousand
    if engine not in costs_per_thousand:
        # Try as if it is a fine-tuned model
        engine = config['gpt_config']['model'].split(':')[0]
        costs_per_thousand = {
            'davinci': 0.1200,
            'curie': 0.0120,
            'babbage': 0.0024,
            'ada': 0.0016
        }
    price = costs_per_thousand[engine] * total_tokens / 1000
    return price


class BatchSizeException(Exception):
    pass
