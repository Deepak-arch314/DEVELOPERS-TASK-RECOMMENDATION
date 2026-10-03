from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def reset_ml_model():
    pass

def get_recommendations_for_developer(developer, tasks, top_n=5):
    if not tasks:
        return []

    dev_skills = " ".join(developer.get("skills", []))
    task_skills = [" ".join(t.get("required_skills", [])) for t in tasks]

    corpus = [dev_skills] + task_skills
    vectorizer = TfidfVectorizer().fit_transform(corpus)
    vectors = vectorizer.toarray()

    dev_vector = vectors[0].reshape(1, -1)
    task_vectors = vectors[1:]

    similarities = cosine_similarity(dev_vector, task_vectors)[0]

    recommendations = []
    for idx, score in enumerate(similarities):
        task = tasks[idx]
        reason = f"Skill match score: {round(score * 100, 1)}%"
        recommendations.append({
            "task": task,
            "recommendation_score": float(score),
            "reason": reason
        })

    recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
    return recommendations[:top_n]