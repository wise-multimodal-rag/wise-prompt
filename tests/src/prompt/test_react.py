import logging
import re

import httpx
import pytest
from langchain_openai import OpenAI

from app.docs.prompt import OPENAI_DEFAULT_MODEL

system_prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

wikipedia:
e.g. wikipedia: Django
Returns a summary from searching Wikipedia

simon_blog_search:
e.g. simon_blog_search: Django
Search Simon's blog for that term

Always look things up on Wikipedia if you have the opportunity to do so.

Example session:

Question: What is the capital of France?
Thought: I should look up France on Wikipedia
Action: wikipedia: France
PAUSE

You will be called again with this:

Observation: France is a country. The capital is Paris.

You then output:

Answer: The capital of France is Paris
""".strip()

action_re = re.compile(r'^Action: (\w+): (.*)$')


class ChatBot:
    def __init__(self, system="", model=OPENAI_DEFAULT_MODEL):
        self.client = OpenAI()
        self.system = system
        self.model = model
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        completion = self.client.chat.completions.create(model=self.model, messages=self.messages)
        # Uncomment this to print out token usage each time, e.g.
        # {"completion_tokens": 86, "prompt_tokens": 26, "total_tokens": 112}
        # print(completion.usage)
        return completion.choices[0].message.content


def react_query(question, max_turns=5):
    i = 0
    bot = ChatBot(system_prompt)
    next_prompt = question
    results = []
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        results.append(result)
        actions = [action_re.match(a) for a in result.split('\n') if action_re.match(a)]
        if actions:
            # There is an action to run
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception("Unknown action: {}: {}".format(action, action_input))
            print(" -- running {} {}".format(action, action_input))
            observation = known_actions[action](action_input)
            print("Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            return '\n'.join(results)


def wikipedia(q):
    return httpx.get("https://en.wikipedia.org/w/api.php", params={
        "action": "query",
        "list": "search",
        "srsearch": q,
        "format": "json"
    }).json()["query"]["search"][0]["snippet"]


def simon_blog_search(q):
    results = httpx.get("https://datasette.simonwillison.net/simonwillisonblog.json", params={
        "sql": """
        select
          blog_entry.title || ': ' || substr(html_strip_tags(blog_entry.body), 0, 1000) as text,
          blog_entry.created
        from
          blog_entry join blog_entry_fts on blog_entry.rowid = blog_entry_fts.rowid
        where
          blog_entry_fts match escape_fts(:q)
        order by
          blog_entry_fts.rank
        limit
          1""".strip(),
        "_shape": "array",
        "q": q,
    }).json()
    return results[0]["text"]


def calculate(what):
    return eval(what)


known_actions = {
    "wikipedia": wikipedia,
    "calculate": calculate,
    "simon_blog_search": simon_blog_search
}

import re

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

model_instructions = """Solve a question answering task with interleaving Thought, Action, Observation steps. Thought can reason about the current situation, Observation is understanding relevant information from an Action's output and Action can be of three types:
(1) entity, which searches the exact entity on Wikipedia and returns the first paragraph if it exists. If not, it will return some similar entities to search and you can try to search the information from those topics.
(2) keyword, which returns the next sentence containing keyword in the current context. This only does exact matches, so keep your searches short.
(3) answer, which returns the answer and finishes the task.
"""
few_shot_prompt = """
Here are some examples.

Question What is the elevation range for the area that the eastern sector of the
Colorado orogeny extends into?
Thought 1 I need to search Colorado orogeny, find the area that the eastern sector
of the Colorado orogeny extends into, then find the elevation range of the
area.
Action 1 Search[Colorado orogeny]
Observation 1 The Colorado orogeny was an episode of mountain building (an orogeny) in
Colorado and surrounding areas.
Thought 2 It does not mention the eastern sector. So I need to look up eastern
sector.
Action 2 Lookup[eastern sector]
Observation 2 (Result 1 / 1) The eastern sector extends into the High Plains and is called
the Central Plains orogeny.
Thought 3 The eastern sector of Colorado orogeny extends into the High Plains. So I
need to search High Plains and find its elevation range.
Action 3 Search[High Plains]
Observation 3 High Plains refers to one of two distinct land regions
Thought 4 I need to instead search High Plains (United States).
Action 4 Search[High Plains (United States)]
Observation 4 The High Plains are a subregion of the Great Plains. From east to west, the
High Plains rise in elevation from around 1,800 to 7,000 ft (550 to 2,130
m).[3]
Thought 5 High Plains rise in elevation from around 1,800 to 7,000 ft, so the answer
is 1,800 to 7,000 ft.
Action 5 Finish[1,800 to 7,000 ft]

Question
{question}"""


class ReAct:
    def __init__(self, model: str, system_prompt: str, prompt: str):
        """Prepares Gemini to follow a `Few-shot ReAct prompt` by imitating
        `function calling` technique to generate both reasoning traces and
        task-specific actions in an interleaved manner.

        Args:
            model: name to the model.
            prompt: ReAct prompt
        """
        self.model = OpenAI()
        self.model_name = model
        self.messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        self.should_continue_prompting = True
        self._search_history: list[str] = []
        self._search_urls: list[str] = []
        self._prompt = prompt

    @property
    def prompt(self):
        return self._prompt

    @classmethod
    def add_method(cls, func):
        setattr(cls, func.__name__, func)

    @staticmethod
    def clean(text: str):
        """Helper function for responses."""
        text = text.replace("\n", " ")
        return text

    def search(self, query: str):
        """Perfoms search on `query` via Wikipedia api and returns its summary.

        Args:
            query: Search parameter to query the Wikipedia API with.

        Returns:
            observation: Summary of Wikipedia search for `query` if found else
            similar search results.
        """
        observation = None
        query = query.strip()
        try:
            # try to get the summary for requested `query` from the Wikipedia
            observation = wikipedia.summary(query, sentences=4, auto_suggest=False)
            wiki_url = wikipedia.page(query, auto_suggest=False).url
            observation = self.clean(observation)
            # if successful, return the first 2-3 sentences from the summary as model's context
            observation = self.model.chat.completions.create(model=self.model_name, messages=[{
                "role": "user",
                "content": f'Return the first 2 or 3 sentences from the following text: {observation}'}])
            observation = observation.text
            # keep track of the model's search history
            self._search_history.append(query)
            self._search_urls.append(wiki_url)
            logging.debug(f"Information Source: {wiki_url}")
        # if the page is ambiguous/does not exist, return similar search phrases for model's context
        except (DisambiguationError, PageError) as e:
            observation = f'Could not find ["{query}"].'
            # get a list of similar search topics
            search_results = wikipedia.search(query)
            observation += f' Similar: {search_results}. You should search for one of those instead.'

        return observation

    def lookup(self, phrase: str, context_length=200):
        """Searches for the `phrase` in the lastest Wikipedia search page
        and returns number of sentences which is controlled by the
        `context_length` parameter.

        Args:
            phrase: Lookup phrase to search for within a page. Generally
            attributes to some specification of any topic.

            context_length: Number of words to consider
            while looking for the answer.

        Returns:
            result: Context related to the `phrase` within the page.
        """
        # get the last searched Wikipedia page and find `phrase` in it.
        page = wikipedia.page(self._search_history[-1], auto_suggest=False)
        page = page.content
        page = self.clean(page)
        start_index = page.find(phrase)
        # extract sentences considering the context length defined
        result = page[max(0, start_index - context_length):start_index + len(phrase) + context_length]
        logging.debug(f"Information Source: {self._search_urls[-1]}")
        return result

    def finish(self, _):
        """Finishes the conversation on encountering  token by
        setting the `self.should_continue_prompting` flag to `False`.
        """
        self.should_continue_prompting = False
        logging.debug(f"Information Sources: {self._search_urls}")

    def __call__(self, user_question, max_calls: int = 3, **generation_kwargs):
        """Starts multi-turn conversation with the chat models with function calling

        Args:
            max_calls: max calls made to the model to get the final answer.

            generation_kwargs: Same as genai.GenerativeModel.GenerationConfig
                    candidate_count: (int | None) = None,
                    stop_sequences: (Iterable[str] | None) = None,
                    max_output_tokens: (int | None) = None,
                    temperature: (float | None) = None,
                    top_p: (float | None) = None,
                    top_k: (int | None) = None

        Raises:
            AssertionError: if max_calls is not between 1 and 8
        """

        # hyperparameter fine-tuned according to the paper
        assert 0 < max_calls <= 8, "max_calls must be between 1 and 8"
        # stop_sequences for the model to immitate function calling
        callable_entities = ['', '', '']
        generation_kwargs.update({'stop_sequences': callable_entities})
        self.should_continue_prompting = True
        for idx in range(max_calls):
            self.messages[1]['content'] = self.prompt.format(question=user_question)
            self.response = self.model.chat.completions.create(model=self.model_name, messages=self.messages)
            response_cmd = self.response.choices[0].message.content
            logging.debug(f"response: {response_cmd}")
            logging.debug(f"Completion Tokens: {self.response.usage.completion_tokens}, "
                          f"Prompt Tokens: {self.response.usage.prompt_tokens}, "
                          f"Total Tokens: {self.response.usage.total_tokens}")
            try:
                # regex to extract
                cmd = re.findall(r'<(.*)>', response_cmd)[-1]
                logging.debug(f'{cmd=}>')
                # regex to extract param
                query = response_cmd.split(f'<{cmd}>')[-1].strip()
                # call to appropriate function
                observation = self.__getattribute__(cmd)(query)
                if not self.should_continue_prompting:
                    break
                stream_message = f"\nObservation {idx + 1}\n{observation}"
                print(stream_message)
                # send function's output as user's response
                model_prompt = f"<{cmd}>{query}{cmd}>'s Output: {stream_message}"
            except (IndexError, AttributeError) as e:
                model_prompt = "Please try to generate thought-action-observation traces as instructed by the prompt."


# Set up the base template
template = """Complete the objective as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

These were previous tasks you completed:



Begin!

Question: {input}
{agent_scratchpad}"""


@pytest.mark.skip(reason="ReAct 직접 구현 로컬 테스트용")
def test_react():
    answer = react_query("What does England share borders with")
    ReAct_chat = ReAct(model=OPENAI_DEFAULT_MODEL, system_prompt=model_instructions, prompt=few_shot_prompt)
    answer = ReAct_chat("코끼리라는 단어의 어원을 알려줘", temperature=0.2)
