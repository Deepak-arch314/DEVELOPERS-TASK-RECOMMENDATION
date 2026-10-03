"""Standalone Machine Learning model class for task recommendations."""
from typing import Dict, List, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TaskRecommenderModel:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()

    def predict(self, developer: Dict[str, Any], tasks: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        if not tasks:
            return []

        dev_skills = " ".join(developer.get("skills", []))
        task_skills = [" ".join(t.get("required_skills", [])) for t in tasks]

        corpus = [dev_skills] + task_skills
        tfidf_matrix = self.vectorizer.fit_transform(corpus)

        dev_vector = tfidf_matrix[0:1]
        task_vectors = tfidf_matrix[1:]

        scores = cosine_similarity(dev_vector, task_vectors)[0]

        results = []
        for idx, score in enumerate(scores):
            results.append({
                "task": tasks[idx],
                "recommendation_score": float(score),
                "reason": f"TF-IDF Skill similarity match: {round(score * 100, 1)}%"
            })

        results.sort(key=lambda x: x["recommendation_score"], reverse=True)
        return results[:top_n]