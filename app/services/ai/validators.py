import json
from pydantic import ValidationError
from app.schemas.chat import AiResponse

class AiValidationError(Exception):
    pass

def parse_and_validate_ai_json(raw: str) -> AiResponse:
    try:
        obj = json.loads(raw)
    except Exception as e:
        raise AiValidationError(f"json_parse_failed: {e}")
    try:
        return AiResponse.model_validate(obj)
    except ValidationError as e:
        raise AiValidationError(f"schema_invalid: {e}")

def enforce_candidate_only(resp: AiResponse, candidate_ids: set[int]) -> AiResponse:
    bad = []
    for r in resp.recommendations:
        if r.dish_id not in candidate_ids:
            bad.append(r.dish_id)
    if resp.combo and resp.combo.enabled:
        for it in resp.combo.items:
            if it.dish_id not in candidate_ids:
                bad.append(it.dish_id)
    if bad:
        raise AiValidationError(f"out_of_candidates: {sorted(set(bad))}")
    return resp
