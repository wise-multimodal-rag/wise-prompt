import logging
import random
from typing import List, Tuple

from app.constants import APETemplate
from app.schemas.ape import ApeResponse, ApeInputOutput
from app.src.ape import generate, evaluate, config, data, llm
from app.src.ape.config import template


def get_simple_prompt_gen_template(prompt_gen_template, prompt_gen_mode):
    """Get Simple Prompt Generation Template"""
    if prompt_gen_template is None:
        if prompt_gen_mode == 'forward':
            prompt_gen_template = APETemplate.PROMPT_GENERATE_TEMPLATE
        elif prompt_gen_mode == 'insert':
            prompt_gen_template = None
        else:
            raise ValueError('Invalid prompt_gen_mode: {}'.format(prompt_gen_mode))
    return prompt_gen_template


def simple_ape(
        prompt_gen_data: Tuple[List[str], List[str]], eval_data: Tuple[List[str], List[str]],
        eval_template=APETemplate.ZERO_SHOT_EVALUATION, demos_template=APETemplate.DEMO_TEMPLATE,
        prompt_gen_template=None, prompt_gen_model: str = 'gpt-4o-mini', eval_model: str = 'gpt-4o-mini',
        prompt_gen_mode: str = 'forward', num_prompts: int = 50, eval_rounds: int = 10,
        prompt_gen_batch_size: int = 200, eval_batch_size: int = 500):
    """Function that wraps the find_prompts function to make it easier to use.

    Design goals: include default values for most parameters, and automatically
    fill out the config dict for the user in a way that fits almost all use cases.

    The main shortcuts this function takes are:
    - Uses the same dataset for prompt generation, evaluation, and few shot demos
    - Uses UCB algorithm for evaluation
    - Fixes the number of prompts per round to num_prompts // 3  (so the first three rounds will sample every prompt once)
    - Fixes the number of samples per prompt per round to 5
    Parameters:
        prompt_gen_data: The dataset to use for prompt generation.
        eval_data: The dataset to use for evaluation
        eval_template: The template for the evaluation queries.
        prompt_gen_template: The template to use for prompt generation.
        demos_template: The template for the demos.
        eval_model: The model to use for evaluation.
        prompt_gen_model: The model to use for prompt generation.
        prompt_gen_mode: The mode to use for prompt generation.
        num_prompts: The number of prompts to generate during the search.
        eval_rounds: The number of evaluation rounds to run.
        prompt_gen_batch_size:
        eval_batch_size:
    Returns:
        An evaluation result and a function to evaluate the prompts with new inputs.
    """
    prompt_gen_template = get_simple_prompt_gen_template(prompt_gen_template, prompt_gen_mode)
    conf = config.simple_config(
        eval_model, prompt_gen_model, prompt_gen_mode, num_prompts, eval_rounds, prompt_gen_batch_size, eval_batch_size)
    return find_prompts(eval_template, demos_template, prompt_gen_data, eval_data, conf,
                        prompt_gen_template=prompt_gen_template)


def simple_eval(
        dataset, prompts, eval_template=APETemplate.ZERO_SHOT_EVALUATION, demos_template=APETemplate.DEMO_TEMPLATE,
        eval_model='gpt-4o-mini', num_samples=50):
    """Function that wraps the evaluate_prompts function to make it easier to use.

    Parameters:
        dataset: The dataset to use for evaluation.
        prompts: The list of prompts to evaluate.
        eval_template: The template for the evaluation queries.
        demos_template: The template for the demos.
        eval_model: The model to use for evaluation.
        num_samples:
    Returns:
        An evaluation result.
    """
    eval_template = template.EvalTemplate(eval_template)
    demos_template = template.DemosTemplate(demos_template)
    conf = config.update_config({}, 'configs/default.yaml')
    conf['evaluation']['model']['gpt_config']['model'] = eval_model
    conf['evaluation']['num_samples'] = min(len(dataset[0]), num_samples)
    res = evaluate.evalute_prompts(
        prompts, eval_template, dataset, demos_template, dataset, conf['evaluation']['method'], conf['evaluation'])
    return res


def simple_estimate_cost(
        dataset, eval_template=APETemplate.ZERO_SHOT_EVALUATION,
        prompt_gen_template=None, demos_template=APETemplate.DEMO_TEMPLATE,
        eval_model='gpt-4o-mini', prompt_gen_model='gpt-4o-mini', prompt_gen_mode='forward',
        num_prompts=50, eval_rounds=10, prompt_gen_batch_size=200, eval_batch_size=500):
    """Simple Estimate Cost func"""
    prompt_gen_template = get_simple_prompt_gen_template(prompt_gen_template, prompt_gen_mode)
    conf = config.simple_config(eval_model, prompt_gen_model, prompt_gen_mode, num_prompts, eval_rounds,
                                prompt_gen_batch_size, eval_batch_size)
    return estimate_cost(eval_template, demos_template, dataset, dataset, conf, prompt_gen_template=prompt_gen_template)


def find_prompts(eval_template, demos_template, prompt_gen_data, eval_data, conf, base_conf='configs/default.yaml',
                 few_shot_data=None, prompt_gen_template=None):
    """Function to generate prompts using APE.

    Parameters:
        eval_template: The template for the evaluation queries.
        demos_template: The template for the demos.
        prompt_gen_data: The data to use for prompt generation.
        eval_data: The data to use for evaluation.
        conf: The configuration dictionary.
        base_conf:
        few_shot_data: The data to use for demonstrations during eval (not implemented yet).
        prompt_gen_template: The template to use for prompt generation.

    Returns:
        An evaluation result. Also returns a function to evaluate the prompts with new inputs.
    """
    conf = config.update_config(conf, base_conf)
    # Generate prompts
    eval_template = template.EvalTemplate(eval_template)
    demos_template = template.DemosTemplate(demos_template)
    if prompt_gen_template is None:
        prompt_gen_template = eval_template.convert_to_generation_template()
    else:
        prompt_gen_template = template.GenerationTemplate(prompt_gen_template)
    if few_shot_data is None:
        few_shot_data = prompt_gen_data
    logging.info('Generating prompts...')
    prompts = generate.generate_prompts(prompt_gen_template, demos_template, prompt_gen_data, conf['generation'])

    logging.info(f'Model returned {len(prompts)} prompts. Deduplicating...')
    prompts = list(set(prompts))
    logging.info(f'Deduplicated to {len(prompts)} prompts. {prompts=}')

    logging.info('Evaluating prompts...')
    result = evaluate.evalute_prompts(prompts, eval_template, eval_data, demos_template, few_shot_data,
                                      conf['evaluation']['method'], conf['evaluation'])
    result = [ApeResponse(prompt=prompt, score=score)
              for prompt, score in zip(result.prompts, result.scores.tolist())]  # pyright: ignore
    logging.info(f'Finished evaluating: {result=}')
    demo_fn = evaluate.demo_function(eval_template, conf['demo'])
    return result, demo_fn


def evaluate_prompts(prompts, eval_template, eval_data, demos_template, few_shot_data, conf,
                     base_conf='configs/default.yaml'):
    """Function to evaluate a list of prompts.

    Parameters:
        prompts: The list of prompts to evaluate.
        eval_template: The template for the evaluation queries.
        eval_data: The data to use for evaluation.
        few_shot_data:
        demos_template:
        conf: The configuration dictionary.
        base_conf: The base configuration file.

    Returns:
        A list of prompts and their scores, sorted by score.
    """
    conf = config.update_config(conf, base_conf)
    # Generate prompts
    eval_template = template.EvalTemplate(eval_template)
    demos_template = template.DemosTemplate(demos_template)
    logging.debug('Evaluating prompts...')
    res = evaluate.evalute_prompts(prompts, eval_template, eval_data, demos_template, few_shot_data,
                                   conf['evaluation']['method'], conf['evaluation'])
    logging.debug('Finished evaluating.')
    return res


def estimate_cost(eval_template, demos_template, prompt_gen_data, eval_data, conf, base_conf='configs/default.yaml',
                  few_shot_data=None, prompt_gen_template=None, eval_query=None):
    """Estimate Cost"""
    conf = config.update_config(conf, base_conf)
    max_prompt_len = conf['generation']['model']['gpt_config']['max_tokens']
    num_prompts = conf['generation']['num_prompts_per_subsample'] * \
                  conf['generation']['num_subsamples']
    eval_method = conf['evaluation']['method']
    if eval_method == 'bandits':
        num_prompts_per_round = conf['evaluation']['num_prompts_per_round']
        if num_prompts_per_round < 1:
            num_prompts_per_round = int(
                num_prompts * num_prompts_per_round)
        num_evals = conf['evaluation']['rounds'] * \
                    num_prompts_per_round * \
                    conf['evaluation']['base_eval_config']['num_samples']
    else:
        num_evals = conf['evaluation']['num_samples'] * num_prompts

    # Compute cost of prompt generation
    queries = get_generation_query(
        eval_template, demos_template, conf, prompt_gen_data, prompt_gen_template, num_query=50)
    query_cost = 0
    for query in queries:
        query_cost += llm.gpt_get_estimated_cost(
            conf['generation']['model'], query, max_prompt_len)
    total_query_cost = query_cost / len(queries) * num_prompts

    # Compute cost of evaluation
    if few_shot_data is None:
        few_shot_data = prompt_gen_data
    queries = get_evaluation_query(
        eval_template, demos_template, conf, eval_data, few_shot_data, eval_query, num_query=50)
    if conf['evaluation']['method'] == 'bandits':
        model_name = conf['evaluation']['base_eval_config']['model']
    else:
        model_name = conf['evaluation']['model']
    query_cost = 0
    for query in queries:
        query_cost += llm.gpt_get_estimated_cost(model_name, query, 0)
    total_eval_cost = query_cost / len(queries) * num_evals
    return total_query_cost + total_eval_cost


def get_generation_query(eval_template, demos_template, conf, prompt_gen_data, prompt_gen_template=None, num_query=1):
    """Generate prompts"""
    eval_template = template.EvalTemplate(eval_template)
    demos_template = template.DemosTemplate(demos_template)
    if prompt_gen_template is None:
        prompt_gen_template = eval_template.convert_to_generation_template()
    else:
        prompt_gen_template = template.GenerationTemplate(prompt_gen_template)
    # First, generate a few prompt queries:
    queries = []
    for _ in range(num_query):
        subsampled_data = data.subsample_data(prompt_gen_data, conf['generation']['num_demos'])
        queries.append(generate.get_query(prompt_gen_template, demos_template, subsampled_data))

    return queries


def get_evaluation_query(eval_template, demos_template, conf, eval_data, few_shot_data, eval_query=None, num_query=1):
    """Get Evaluation Query"""
    eval_template = template.EvalTemplate(eval_template)
    demos_template = template.DemosTemplate(demos_template)

    if conf['evaluation']['method'] == 'bandits':
        eval_base_method = conf['evaluation']['base_eval_method']
        num_few_shot = conf['evaluation']['base_eval_config']['num_few_shot']
    else:
        eval_base_method = conf['evaluation']['method']
        num_few_shot = conf['evaluation']['num_few_shot']

    if eval_query is None:
        if eval_base_method == 'likelihood':
            from app.src.ape.evaluation import likelihood
            eval_query = likelihood.get_query
        else:
            raise ValueError('Cannot estimate costs for: {}'.format(eval_base_method))

    max_prompt_len = conf['generation']['model']['gpt_config']['max_tokens']
    filler_prompt = 'GGGG' * max_prompt_len

    queries = []
    for _ in range(num_query):
        idx = random.randint(0, len(eval_data[0]) - 1)
        input_, output_ = eval_data[0][idx], eval_data[1][idx]
        demo_data = data.subsample_data(few_shot_data, num_few_shot)
        query = eval_query(filler_prompt, eval_template, input_, output_, demo_data, demos_template)[0]
        queries.append(query)
    return queries


def ape(prompt_gen_data: ApeInputOutput, eval_data: ApeInputOutput, prompt_gen_model: str, eval_model: str,
        num_prompts: int, eval_rounds: int, prompt_gen_batch_size: int, eval_batch_size: int):
    """APE"""
    result, demo_fn = simple_ape(
        prompt_gen_data=(prompt_gen_data.inputs, prompt_gen_data.outputs),
        eval_data=(eval_data.inputs, eval_data.outputs),
        eval_template=APETemplate.ZERO_SHOT_EVALUATION,
        prompt_gen_model=prompt_gen_model, eval_model=eval_model, num_prompts=num_prompts,
        eval_rounds=eval_rounds, prompt_gen_batch_size=prompt_gen_batch_size, eval_batch_size=eval_batch_size)
    return result
