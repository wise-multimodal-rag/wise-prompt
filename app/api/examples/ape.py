from app.schemas.models import ApeRequest, ApeInputOutput

ape_default_example = {
    "summary": "APE 기본 예제",
    "description": "APE 기본 예제",
    "value": ApeRequest(
        prompt_gen_data=ApeInputOutput(
            inputs=["sane", "direct", "informally", "unpopular", "subtractive", "nonresidential", "inexact", "uptown",
                    "incomparable", "powerful", "gaseous", "evenly", "formality", "deliberately", "off"],
            outputs=["insane", "indirect", "formally", "popular", "additive", "residential", "exact", "downtown",
                     "comparable", "powerless", "solid", "unevenly", "informality", "accidentally", "on"]),
        eval_data=ApeInputOutput(
            inputs=["appear", "ability", "bitter", "attach", "affirmative", "bitter", "antipathy", "consumer",
                    "conceal", "cheap", "conscious", "content", "comedy", "construct", "birth"],
            outputs=["disappear", "inability", "sweet", "detach", "negative", "sweet", "sympathy", "producer",
                     "reveal", "expensive", "unconscious", "malcontent", "tragedy", "destroy", "death"])
    )
}
ape_examples = {
    "ape_default": ape_default_example
}
