import random
from typing import List, Tuple, Dict
from .model import TagFile
from .parse import parse_tag_expression, evaluate_ast, is_ast_expression

def rating_filter(files: List[TagFile], rating: str) -> List[TagFile]:
    allowed = {"g"} if rating=="g" else {"g","p"} if rating=="p" else {"g","p","r"}
    return [f for f in files if f.rating in allowed]

def pick_random_tags(files: List[TagFile], n: int) -> List[Tuple[str, str]]:
    plain_tags = [(tag, f.name)
                  for f in files for tag in f.tags
                  if not is_ast_expression(tag)]
    return random.sample(plain_tags, min(n, len(plain_tags)))

def pick_tags_by_template(files: List[TagFile], values: Dict[str, int]) -> List[Tuple[str, str]]:
    files_by_name = {f.name: f for f in files}
    results = []
    for file_name, n in values.items():
        f_obj = files_by_name.get(file_name)
        if not f_obj or n <= 0: continue
        for _ in range(n):
            tag_line = random.choice(f_obj.tags)
            ast = parse_tag_expression(tag_line)
            picked_tags = evaluate_ast(ast, files_by_name)
            results.extend((t, f_obj.name) for t in picked_tags)
    return results
