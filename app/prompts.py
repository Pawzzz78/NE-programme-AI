SYSTEM_PROMPT = """Tu es un assistant d'information citoyenne sur le programme de David Lisnard (Nouvelle Énergie).

RÈGLES STRICTES :
1. Tu réponds UNIQUEMENT à partir des EXTRAITS fournis dans le message utilisateur.
2. Tu n'utilises aucune connaissance externe (actualité, Wikipedia, autres candidats, spéculations).
3. Chaque affirmation importante doit être suivie d'une citation courte entre guillemets tirée d'un extrait, puis de la source au format :
   [Source : {page_title} — {section} — paragraphe {paragraph} — {url}]
4. Si les extraits ne permettent pas de répondre, réponds exactement :
   « Aucune réponse trouvée dans le programme officiel. »
   sans inventer ni compléter.
5. Style : français clair, factuel, concis. Pas de slogan partisan ajouté par toi.
6. Tu peux synthétiser plusieurs extraits, mais sans déformer ni extrapoler.
"""


def build_user_prompt(question: str, chunks: list[dict]) -> str:
    if not chunks:
        return (
            f"Question : {question}\n\n"
            "Aucun extrait pertinent n'a été trouvé dans le corpus du site officiel.\n"
            "Réponds uniquement : « Aucune réponse trouvée dans le programme officiel. »"
        )

    blocks = []
    for i, c in enumerate(chunks, 1):
        blocks.append(
            f"--- EXTRAIT {i} ---\n"
            f"page_title: {c['page_title']}\n"
            f"section: {c['section']}\n"
            f"paragraph: {c['paragraph']}\n"
            f"url: {c['url']}\n"
            f"texte:\n{c['text']}\n"
        )
    return (
        f"Question : {question}\n\n"
        "Extraits du site officiel unenouvelleenergie.fr uniquement :\n\n"
        + "\n".join(blocks)
        + "\nRéponds en citant les sources (page, section, paragraphe, url)."
    )
