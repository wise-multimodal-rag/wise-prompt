import logging
import random
from pathlib import Path
from typing import List, Dict

from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

from app.constants import MagicSentence, PromptTemplate
from app.schemas.models import LLMProviderRequest
from app.exceptions.service import InvalidDomainError
from app.src.llm_provider.llm_tool import model_setting


def get_cot_dataset(dataset_path):
    """

    Args:
        dataset_path:

    Returns:

    # TODO: 도메인별 데이터셋 설정, 미리 예제 생성? 사용자에게 직접 파일로 받아오기?
    """
    corpus = []
    question = []
    rationale = []
    pred_ans = []
    with open(dataset_path, "r", encoding="utf-8") as fp:
        answer_seg = ""
        for line in fp:
            if "Q: " in line:
                c_question: str = line.strip()
            if "A: " in line:
                answer_seg = line
            elif "Therefore" in line and "the answer" in line:
                c_rationale = answer_seg
            elif answer_seg != "":
                answer_seg += line
            if "pred_mode" in line:
                c_pred_ans = line.split(":")[1].strip()
                c_rationale = c_rationale.replace(f"A: {MagicSentence.COT_DEFAULT_MAGIC_SENTENCE}",
                                                  MagicSentence.COT_DEFAULT_MAGIC_SENTENCE)
                c_question = c_question + "\nA:"  # pyright: ignore
                corpus.append(c_question)
                question.append(c_question)
                rationale.append(c_rationale)
                pred_ans.append(c_pred_ans)
                answer_seg = ""
    return corpus, question, rationale, pred_ans


def kmeans_clustering(num_clusters, corpus, corpus_embeddings, random_seed):
    clustering_model = KMeans(n_clusters=num_clusters, random_state=random_seed)
    # 각 문장이 할당된 클러스터를 나타내는 레이블 리스트 저장
    clustering_model.fit(corpus_embeddings)
    cluster_assignment = clustering_model.labels_
    logging.debug(f"{cluster_assignment=}")
    clustered_sentences: List[List[float]] = [[] for i in range(num_clusters)]
    logging.debug(f"{clustered_sentences=}")
    # 각 문장이 각 클러스터의 중심(centroid)에서 얼마나 떨어져 있는지 계산 (문장 수 x 클러스터 수)
    dist = clustering_model.transform(corpus_embeddings)
    clustered_dists: List[List[float]] = [[] for i in range(num_clusters)]
    clustered_idx: List[List[int]] = [[] for i in range(num_clusters)]
    # cluster_assignment를 순회하면서 각 문장의 ID(sentence_id)와 할당된 클러스터 ID(cluster_id)를 이용하여 해당 클러스터에 문장, 거리 및 인덱스 저장
    for sentence_id, cluster_id in enumerate(cluster_assignment):  # pyright: ignore
        clustered_sentences[cluster_id].append(corpus[sentence_id])
        clustered_dists[cluster_id].append(dist[sentence_id][cluster_id])
        clustered_idx[cluster_id].append(sentence_id)
    logging.debug(f"{clustered_dists=}")
    logging.debug(f"{clustered_idx=}")
    return clustered_dists, clustered_idx


def get_cluster_center(clustered_dists, clustered_idx, rationale, pred_ans, question, max_ra_len) -> List[
    Dict[str, str]]:
    sampling_method = "center"
    task = "multiarith"  # TODO: 태스크 설정
    demos = []
    for i in range(len(clustered_dists)):
        # [문장 인덱스, 거리] 형태의 리스트들
        tmp = list(map(list, zip(range(len(clustered_dists[i])), clustered_dists[i])))
        # tmp 리스트를 거리를 기준으로 오름차순(reverse=False)으로 정렬합니다. 즉, 중심에서 가장 가까운 문장이 리스트의 앞쪽에 오도록 정렬됩니다.
        top_min_dist = sorted(tmp, key=lambda x: x[1], reverse=False)
        if not sampling_method == "center":
            random.shuffle(top_min_dist)
        for element in top_min_dist:
            min_idx = element[0]
            c_rationale = rationale[clustered_idx[i][min_idx]].strip()
            c_pred_ans = pred_ans[clustered_idx[i][min_idx]].strip()

            if len(question[clustered_idx[i][min_idx]].strip().split()) <= 60 \
                    and len(c_rationale.replace("\n\n", "\n").split("\n")) <= max_ra_len and c_rationale[
                -1] == "." and c_pred_ans != "":
                if task in ["gsm8k", "multiarith", "singleeq", "addsub", "svamp"]:
                    if not (c_pred_ans.strip() in c_rationale.split(".")[
                        -2] or c_pred_ans.strip() in c_rationale.split()[-10:]):
                        continue
                c_question = question[clustered_idx[i][min_idx]]
                c_rationale = c_rationale.replace("\n\n", "\n").replace("\n", " ").strip()
                c_rationale = " ".join(c_rationale.split())
                demo_element = {
                    "question": c_question,
                    "rationale": c_rationale,
                    "pred_ans": c_pred_ans,
                }
                demos.append(demo_element)
                break
    logging.debug(f"{demos=}")
    return demos


def embeddings(corpus, encoder_name):
    encoder = SentenceTransformer(encoder_name)
    corpus_embeddings = encoder.encode(corpus)
    return corpus_embeddings


def question_clustering(domain: str, encoder_name, n_clusters, random_seed, max_ra_len):
    # TODO: demonstration&answer dataset 어떻게 받을지, 형식 지정?,
    dataset_path = f"./dataset/{domain.replace(' ', '_')}_zero_shot_cot.log"
    if not Path(dataset_path).exists():
        raise InvalidDomainError(domain)
    corpus, question, rationale, pred_ans = get_cot_dataset(dataset_path)
    corpus_embeddings = embeddings(corpus, encoder_name)
    clustered_dists, clustered_idx = kmeans_clustering(n_clusters, corpus, corpus_embeddings, random_seed)
    demos: List[Dict[str, str]] = get_cluster_center(clustered_dists, clustered_idx, rationale, pred_ans, question,
                                                     max_ra_len)
    return demos


def demonstration_sampling(demos: List[Dict[str, str]], system_prompt, prompt, llm_provider):
    examples = [f"""{demo['question']} {demo['rationale']} The answer is {demo['pred_ans']}""" for demo in demos]
    logging.debug(f"Question {examples=}")
    model = model_setting(llm_provider.llm_tool, llm_provider.model, llm_provider.temperature)
    chain = PromptTemplate.AUTO_COT | model
    result = chain.invoke(
        {"system_prompt": system_prompt, "prompt": prompt,
         "examples": examples, "magic_sentence": MagicSentence.COT_DEFAULT_MAGIC_SENTENCE}
    )
    return result.content


def auto_cot_prompt(domain: str, system_prompt, prompt, llm_provider: LLMProviderRequest, encoder, n_clusters,
                    random_seed, max_ra_len):
    demos: List[Dict[str, str]] = question_clustering(domain, encoder, n_clusters, random_seed, max_ra_len)
    answer = demonstration_sampling(demos, system_prompt, prompt, llm_provider)
    return answer
